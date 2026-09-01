from typing import Optional, List, Dict, Any
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.admission_links import AdmissionLinks


class AdmissionLinksService:
    """
    处理 AdmissionLinks 相关的业务逻辑
    表: admission_links - 学校申请链接表
    """

    async def fetch(self, db: AsyncSession, id: int) -> Optional[AdmissionLinks]:
        """
        根据 ID 查询记录
        :param db: 异步数据库会话
        :param id: 记录ID
        :return: AdmissionLinks 对象或 None
        """
        statement = select(AdmissionLinks).where(AdmissionLinks.id == id)
        result = await db.exec(statement)
        return result.first()

    async def list(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[AdmissionLinks]:
        """
        分页查询记录列表
        :param db: 异步数据库会话
        :param skip: 跳过记录数
        :param limit: 返回记录数
        :return: AdmissionLinks 列表
        """
        statement = select(AdmissionLinks).offset(skip).limit(limit)
        result = await db.exec(statement)
        return result.all()

    async def query_list(
        self, 
        db: AsyncSession, 
        condition: Dict[str, Any], 
        order_by: Optional[str] = None, 
        sort_by: Optional[str] = "asc"
    ) -> List[AdmissionLinks]:
        """
        根据条件查询记录列表
        :param db: 异步数据库会话
        :param condition: 查询条件字典
        :param order_by: 排序字段
        :param sort_by: 排序方式 ('asc' or 'desc')
        :return: AdmissionLinks 列表
        """
        statement = select(AdmissionLinks)
        for key, value in condition.items():
            if hasattr(AdmissionLinks, key):
                statement = statement.where(getattr(AdmissionLinks, key) == value)
        
        if order_by and hasattr(AdmissionLinks, order_by):
            order_col = getattr(AdmissionLinks, order_by)
            if sort_by and sort_by.lower() == 'desc':
                statement = statement.order_by(order_col.desc())
            else:
                statement = statement.order_by(order_col.asc())
        
        result = await db.exec(statement)
        return result.all()

    async def query_one(self, db: AsyncSession, condition: Dict[str, Any]) -> Optional[AdmissionLinks]:
        """
        根据条件查询单条记录
        :param db: 异步数据库会话
        :param condition: 查询条件字典
        :return: AdmissionLinks 对象或 None
        """
        statement = select(AdmissionLinks)
        for key, value in condition.items():
            if hasattr(AdmissionLinks, key):
                statement = statement.where(getattr(AdmissionLinks, key) == value)
        
        result = await db.exec(statement)
        return result.first()

    async def create(self, db: AsyncSession, admission_links: AdmissionLinks) -> AdmissionLinks:
        """
        创建新记录
        :param db: 异步数据库会话
        :param admission_links: 要创建的记录对象
        :return: 创建后的记录对象
        """
        db.add(admission_links)
        await db.flush()
        return admission_links

    async def update(self, db: AsyncSession, admission_links: AdmissionLinks) -> AdmissionLinks:
        """
        更新记录
        :param db: 异步数据库会话
        :param admission_links: 要更新的记录对象
        :return: 更新后的记录对象
        """
        db.add(admission_links)
        await db.flush()
        return admission_links

    async def delete(self, db: AsyncSession, id: int) -> bool:
        """
        删除记录
        :param db: 异步数据库会话
        :param id: 记录ID
        :return: 是否删除成功
        """
        admission_links = await self.fetch(db, id)
        if admission_links:
            await db.delete(admission_links)
            await db.flush()
            return True
        return False

# 创建单例实例 (Singleton)
admission_links_service = AdmissionLinksService()