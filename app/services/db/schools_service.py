from typing import Optional, List, Dict, Any
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.schools import Schools


class SchoolsService:
    """
    处理 Schools 相关的业务逻辑
    表: schools - 香港学校信息表
    """

    async def fetch(self, db: AsyncSession, id: int) -> Optional[Schools]:
        """
        根据 ID 查询记录
        :param db: 异步数据库会话
        :param id: 记录ID
        :return: Schools 对象或 None
        """
        statement = select(Schools).where(Schools.id == id)
        result = await db.exec(statement)
        return result.first()

    async def list(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Schools]:
        """
        分页查询记录列表
        :param db: 异步数据库会话
        :param skip: 跳过记录数
        :param limit: 返回记录数
        :return: Schools 列表
        """
        statement = select(Schools).offset(skip).limit(limit)
        result = await db.exec(statement)
        return result.all()

    async def query_list(
        self, 
        db: AsyncSession, 
        condition: Dict[str, Any], 
        order_by: Optional[str] = None, 
        sort_by: Optional[str] = "asc"
    ) -> List[Schools]:
        """
        根据条件查询记录列表
        :param db: 异步数据库会话
        :param condition: 查询条件字典
        :param order_by: 排序字段
        :param sort_by: 排序方式 ('asc' or 'desc')
        :return: Schools 列表
        """
        statement = select(Schools)
        for key, value in condition.items():
            if hasattr(Schools, key):
                statement = statement.where(getattr(Schools, key) == value)
        
        if order_by and hasattr(Schools, order_by):
            order_col = getattr(Schools, order_by)
            if sort_by and sort_by.lower() == 'desc':
                statement = statement.order_by(order_col.desc())
            else:
                statement = statement.order_by(order_col.asc())
        
        result = await db.exec(statement)
        return result.all()

    async def query_one(self, db: AsyncSession, condition: Dict[str, Any]) -> Optional[Schools]:
        """
        根据条件查询单条记录
        :param db: 异步数据库会话
        :param condition: 查询条件字典
        :return: Schools 对象或 None
        """
        statement = select(Schools)
        for key, value in condition.items():
            if hasattr(Schools, key):
                statement = statement.where(getattr(Schools, key) == value)
        
        result = await db.exec(statement)
        return result.first()

    async def create(self, db: AsyncSession, schools: Schools) -> Schools:
        """
        创建新记录
        :param db: 异步数据库会话
        :param schools: 要创建的记录对象
        :return: 创建后的记录对象
        """
        db.add(schools)
        await db.flush()
        return schools

    async def update(self, db: AsyncSession, schools: Schools) -> Schools:
        """
        更新记录
        :param db: 异步数据库会话
        :param schools: 要更新的记录对象
        :return: 更新后的记录对象
        """
        db.add(schools)
        await db.flush()
        return schools

    async def delete(self, db: AsyncSession, id: int) -> bool:
        """
        删除记录
        :param db: 异步数据库会话
        :param id: 记录ID
        :return: 是否删除成功
        """
        schools = await self.fetch(db, id)
        if schools:
            await db.delete(schools)
            await db.flush()
            return True
        return False

# 创建单例实例 (Singleton)
schools_service = SchoolsService()