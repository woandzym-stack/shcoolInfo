from datetime import datetime
from sqlalchemy import Column
from sqlalchemy import DateTime, Integer, String
from sqlmodel import SQLModel, Field
from typing import Optional


class Schools(SQLModel, table=True):
    """香港学校信息表"""
    __tablename__ = "schools"

    id: int = Field(sa_column=Column("id", Integer, primary_key=True, autoincrement=True))
    # 学校名称
    name: str = Field(sa_column=Column("name", String(255), nullable=False))
    # 学校网址
    url: Optional[str] = Field(default=None, sa_column=Column("url", String(500)))
    # 学校类型
    type: Optional[str] = Field(default=None, sa_column=Column("type", String(50)))
    # 地区
    district: Optional[str] = Field(default=None, sa_column=Column("district", String(50)))
    # 学校组别
    banding: Optional[str] = Field(default=None, sa_column=Column("banding", String(20)))
    # 教学语言
    language: Optional[str] = Field(default=None, sa_column=Column("language", String(50)))
    # 性别
    gender: Optional[str] = Field(default=None, sa_column=Column("gender", String(20)))
    # 宗教
    religion: Optional[str] = Field(default=None, sa_column=Column("religion", String(100)))
    # 地址
    address: Optional[str] = Field(default=None, sa_column=Column("address", String(500)))
    # 电话
    phone: Optional[str] = Field(default=None, sa_column=Column("phone", String(50)))
    # 电邮
    email: Optional[str] = Field(default=None, sa_column=Column("email", String(255)))
    # 申请链接
    admission_link: Optional[str] = Field(default=None, sa_column=Column("admission_link", String(500)))
    created_at: datetime = Field(sa_column=Column("created_at", DateTime, nullable=False))
    updated_at: datetime = Field(sa_column=Column("updated_at", DateTime, nullable=False))