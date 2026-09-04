from typing import Optional, List, Dict, Any
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.weekly_run_log import WeeklyRunLog


class WeeklyRunLogService:
    """
    处理 WeeklyRunLog 相关的业务逻辑
    表: weekly_run_log - 每周刷新流水线运行日志
    """

    async def fetch(self, db: AsyncSession, id: int) -> Optional[WeeklyRunLog]:
        """
        根据 ID 查询记录
        :param db: 异步数据库会话
        :param id: 记录ID
        :return: WeeklyRunLog 对象或 None
        """
        statement = select(WeeklyRunLog).where(WeeklyRunLog.id == id)
        result = await db.exec(statement)
        return result.first()

    async def list(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[WeeklyRunLog]:
        """
        分页查询记录列表
        :param db: 异步数据库会话
        :param skip: 跳过记录数
        :param limit: 返回记录数
        :return: WeeklyRunLog 列表
        """
        statement = select(WeeklyRunLog).offset(skip).limit(limit)
        result = await db.exec(statement)
        return result.all()

    async def query_list(
        self, 
        db: AsyncSession, 
        condition: Dict[str, Any], 
        order_by: Optional[str] = None, 
        sort_by: Optional[str] = "asc"
    ) -> List[WeeklyRunLog]:
        """
        根据条件查询记录列表
        :param db: 异步数据库会话
        :param condition: 查询条件字典
        :param order_by: 排序字段
        :param sort_by: 排序方式 ('asc' or 'desc')
        :return: WeeklyRunLog 列表
        """
        statement = select(WeeklyRunLog)
        for key, value in condition.items():
            if hasattr(WeeklyRunLog, key):
                statement = statement.where(getattr(WeeklyRunLog, key) == value)
        
        if order_by and hasattr(WeeklyRunLog, order_by):
            order_col = getattr(WeeklyRunLog, order_by)
            if sort_by and sort_by.lower() == 'desc':
                statement = statement.order_by(order_col.desc())
            else:
                statement = statement.order_by(order_col.asc())
        
        result = await db.exec(statement)
        return result.all()

    async def query_one(self, db: AsyncSession, condition: Dict[str, Any]) -> Optional[WeeklyRunLog]:
        """
        根据条件查询单条记录
        :param db: 异步数据库会话
        :param condition: 查询条件字典
        :return: WeeklyRunLog 对象或 None
        """
        statement = select(WeeklyRunLog)
        for key, value in condition.items():
            if hasattr(WeeklyRunLog, key):
                statement = statement.where(getattr(WeeklyRunLog, key) == value)
        
        result = await db.exec(statement)
        return result.first()

    async def create(self, db: AsyncSession, weekly_run_log: WeeklyRunLog) -> WeeklyRunLog:
        """
        创建新记录
        :param db: 异步数据库会话
        :param weekly_run_log: 要创建的记录对象
        :return: 创建后的记录对象
        """
        db.add(weekly_run_log)
        await db.flush()
        return weekly_run_log

    async def update(self, db: AsyncSession, weekly_run_log: WeeklyRunLog) -> WeeklyRunLog:
        """
        更新记录
        :param db: 异步数据库会话
        :param weekly_run_log: 要更新的记录对象
        :return: 更新后的记录对象
        """
        db.add(weekly_run_log)
        await db.flush()
        return weekly_run_log

    async def delete(self, db: AsyncSession, id: int) -> bool:
        """
        删除记录
        :param db: 异步数据库会话
        :param id: 记录ID
        :return: 是否删除成功
        """
        weekly_run_log = await self.fetch(db, id)
        if weekly_run_log:
            await db.delete(weekly_run_log)
            await db.flush()
            return True
        return False

# 创建单例实例 (Singleton)
weekly_run_log_service = WeeklyRunLogService()