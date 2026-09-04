import asyncio
import json
import time
from collections import defaultdict
from typing import Annotated, Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from loguru import logger
from opencc import OpenCC
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.db import AsyncSessionLocal, get_async_db
from app.models.admission_links import AdmissionLinks
from app.models.schools import Schools
from app.schemas.response import SingleResponse
from app.services.db import weekly_run_log_service

router = APIRouter()

# ---------- 名录缓存 ----------
# 学校名录是准静态数据（由导入脚本线下更新），而远端库性能较弱
# （两次全表查询 ~0.9s，3800 行 ORM 物化再花数百 ms），因此把序列化后的
# 完整响应体缓存在进程内：命中时 ~1ms，不再触碰数据库。
# 一致性策略：TTL 兜底 + 导入数据后用 ?refresh=1 主动刷新。
_CACHE_TTL_SECONDS = 600
_cache_lock = asyncio.Lock()
_cache_body: Optional[bytes] = None
_cache_data: Optional[List[Dict[str, Any]]] = None
_cache_expires_at: float = 0.0

# 数据库中的校名均为繁体，用户可能输入简体：统一转繁后再匹配。
# s2t 对已是繁体的字符原样保留，因此混合输入也安全。
_cc_s2t = OpenCC("s2t")


async def _load_directory() -> List[Dict[str, Any]]:
    """
    从数据库加载全量名录并组装为响应结构。

    - 只查询页面需要的列，避免 3800 行 SQLModel ORM 对象物化的开销
    - 两表查询用独立会话并发执行（远端库 RTT 高，串行要付两次往返）
    - 只读查询不开事务、不 commit（省去每次一轮的 COMMIT 往返）
    """
    schools_stmt = select(
        Schools.id,
        Schools.name,
        Schools.url,
        Schools.type,
        Schools.district,
        Schools.stage,
        Schools.banding,
        Schools.school_net,
        Schools.language,
        Schools.gender,
        Schools.religion,
        Schools.address,
        Schools.phone,
        Schools.email,
    ).order_by(Schools.id)
    links_stmt = select(
        AdmissionLinks.school_id,
        AdmissionLinks.url,
        AdmissionLinks.link_text,
        AdmissionLinks.grades,
    ).order_by(AdmissionLinks.id)

    async with AsyncSessionLocal() as school_session, AsyncSessionLocal() as link_session:
        schools_result, links_result = await asyncio.gather(
            school_session.exec(schools_stmt),
            link_session.exec(links_stmt),
        )
        school_rows = schools_result.all()
        link_rows = links_result.all()

    links_by_school: Dict[int, List[Dict[str, Any]]] = defaultdict(list)
    for school_id, url, link_text, grades in link_rows:
        links_by_school[school_id].append(
            {
                "url": url,
                "link_text": link_text,
                "grades": grades,
            }
        )

    data: List[Dict[str, Any]] = []
    for row in school_rows:
        (
            s_id, name, url, s_type, district, stage, banding, school_net,
            language, gender, religion, address, phone, email,
        ) = row
        data.append(
            {
                "id": s_id,
                "name": name,
                "url": url,
                "type": s_type,
                "district": district,
                "stage": stage,
                "banding": banding,
                "school_net": school_net,
                "language": language,
                "gender": gender,
                "religion": religion,
                "address": address,
                "phone": phone,
                "email": email,
                "admission_links": links_by_school.get(s_id, []),
            }
        )
    return data


def _serialize(data: List[Dict[str, Any]]) -> bytes:
    """与 SingleResponse 一致的响应信封，序列化一次、缓存复用。"""
    return json.dumps(
        {"data": data, "errCode": 200, "errMsg": None},
        ensure_ascii=False,
    ).encode("utf-8")


async def _get_directory(refresh: bool = False) -> List[Dict[str, Any]]:
    """
    获取全量名录（缓存命中直接返回内存中的 list）。

    - 与 list_schools 共用同一份缓存与重建逻辑，避免两处代码漂移
    - 重建时同时保存序列化字节（整页响应复用）和 list（搜索过滤用）
    """
    global _cache_body, _cache_data, _cache_expires_at

    if not refresh and _cache_data is not None and time.monotonic() < _cache_expires_at:
        return _cache_data

    # 防止缓存过期瞬间的并发请求同时打穿到数据库（thundering herd）
    async with _cache_lock:
        # 二次检查：等锁期间可能已有请求完成了刷新
        if not refresh and _cache_data is not None and time.monotonic() < _cache_expires_at:
            return _cache_data

        t0 = time.perf_counter()
        data = await _load_directory()
        _cache_data = data
        _cache_body = _serialize(data)
        _cache_expires_at = time.monotonic() + _CACHE_TTL_SECONDS

        elapsed_ms = (time.perf_counter() - t0) * 1000
        link_total = sum(len(s["admission_links"]) for s in data)
        logger.info(
            f"学校名录缓存已重建 | 学校数={len(data)} | 插班链接数={link_total} "
            f"| 耗时={elapsed_ms:.0f}ms | 响应体={len(_cache_body) / 1024:.0f}KB"
        )
        return data


@router.get("", response_model=SingleResponse, summary="获取全部学校及插班链接")
async def list_schools(refresh: bool = False) -> Response:
    """
    全量返回学校列表（中学 + 小学），每所学校内嵌 admission_links 数组。

    - 数据量约千所，由前端一次性加载后按学段筛选/分页
    - stage: secondary=中学 / primary=小学；school_net 仅小学有值（'0' 表示不参与派位校网的直资/私立）
    - 插班链接只以 admission_links 表为准（schools.admission_link 字段已废弃）
    - 响应体进程内缓存 10 分钟；导入新数据后请求 ?refresh=1 可立即重建缓存
    - 直接返回序列化好的 Response（绕开 response_model 逐对象校验），结构与 SingleResponse 一致
    """
    if not refresh and _cache_body is not None and time.monotonic() < _cache_expires_at:
        return Response(content=_cache_body, media_type="application/json")

    await _get_directory(refresh=refresh)
    return Response(content=_cache_body, media_type="application/json")


@router.get("/last-updated", response_model=SingleResponse, summary="获取名录最近数据更新时间")
async def last_updated(db: Annotated[AsyncSession, Depends(get_async_db)]) -> SingleResponse:
    """
    返回 weekly_run_log 中最近一次成功运行的完成时间，供页面展示「数据更新于」。

    - 优先取 finished_at；为空时退回 started_at / run_date
    - 表极小（每周一条），不走名录缓存，直接查询
    - 暂无成功记录时 data 为 null，前端应隐藏该展示位
    """
    log = await weekly_run_log_service.latest_success(db)
    if log is None:
        return SingleResponse(data=None)
    ts = log.finished_at or log.started_at or log.run_date
    return SingleResponse(data={"updated_at": ts})


@router.get("/search", response_model=SingleResponse, summary="按名称搜索学校（自动简转繁）")
async def search_schools(
    name: str = Query(..., min_length=1, description="学校名称关键字，简体/繁体均可"),
) -> SingleResponse:
    """
    按名称模糊搜索学校：先把关键字简体转繁体，再与名录中的繁体校名做不区分大小写的子串匹配。

    - 匹配在进程内缓存的名录数据上进行，不触碰数据库
    - 返回结构与 /schools 单条记录一致（含 admission_links），便于前端复用同一渲染逻辑
    """
    kw = _cc_s2t.convert(name).strip().lower()
    if not kw:
        return SingleResponse(data=[])

    data = await _get_directory()
    matched = [s for s in data if kw in (s["name"] or "").lower()]
    return SingleResponse(data=matched)
