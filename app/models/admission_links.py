from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Integer, String
from sqlmodel import Field, SQLModel


class AdmissionLinks(SQLModel, table=True):
    """学校申请链接表"""
    __tablename__ = "admission_links"

    id: int = Field(sa_column=Column("id", Integer, primary_key=True, autoincrement=True))
    # 关联 schools.id
    school_id: int = Field(sa_column=Column("school_id", Integer, nullable=False))
    # 申请链接
    url: str = Field(sa_column=Column("url", String(500), nullable=False))
    # 适用年级，逗号分隔，P1-P6（小学）/ S1-S6（中学），all 表示链接未标注年级
    grades: str = Field(default="all", sa_column=Column("grades", String(100), nullable=False))
    # 链接锚点文字
    link_text: Optional[str] = Field(default=None, sa_column=Column("link_text", String(255)))
    created_at: datetime = Field(sa_column=Column("created_at", DateTime, nullable=False))