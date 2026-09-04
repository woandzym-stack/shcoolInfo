from datetime import date, datetime
from sqlalchemy import Column
from sqlalchemy import Date, DateTime, Integer, String
from sqlmodel import SQLModel, Field
from typing import Optional


class WeeklyRunLog(SQLModel, table=True):
    """每周刷新流水线运行日志"""
    __tablename__ = "weekly_run_log"

    id: int = Field(sa_column=Column("id", Integer, primary_key=True, autoincrement=True))
    # 运行日期
    run_date: date = Field(sa_column=Column("run_date", Date, nullable=False))
    # 开始时间
    started_at: Optional[datetime] = Field(default=None, sa_column=Column("started_at", DateTime))
    # 结束时间
    finished_at: Optional[datetime] = Field(default=None, sa_column=Column("finished_at", DateTime))
    # 耗时（秒）
    duration_sec: Optional[int] = Field(default=None, sa_column=Column("duration_sec", Integer))
    # running/success/failed
    status: str = Field(default="running", sa_column=Column("status", String(20), nullable=False))
    # 中学数（运行后库内总数）
    schools_secondary: Optional[int] = Field(default=None, sa_column=Column("schools_secondary", Integer))
    # 小学数（运行后库内总数）
    schools_primary: Optional[int] = Field(default=None, sa_column=Column("schools_primary", Integer))
    # 重抓后链接总数
    links_after_refetch: Optional[int] = Field(default=None, sa_column=Column("links_after_refetch", Integer))
    # 最终存活链接数
    links_final: Optional[int] = Field(default=None, sa_column=Column("links_final", Integer))
    # 自动删除噪音数
    noise_deleted: Optional[int] = Field(default=None, sa_column=Column("noise_deleted", Integer))
    # 自动删除死链数
    dead_deleted: Optional[int] = Field(default=None, sa_column=Column("dead_deleted", Integer))
    # 留人工复核数
    review_count: Optional[int] = Field(default=None, sa_column=Column("review_count", Integer))
    # 删除备份文件
    backup_file: Optional[str] = Field(default=None, sa_column=Column("backup_file", String(255)))
    # 人工复核清单文件
    review_file: Optional[str] = Field(default=None, sa_column=Column("review_file", String(255)))
    # 异常说明
    note: Optional[str] = Field(default=None, sa_column=Column("note", String(500)))
    created_at: datetime = Field(sa_column=Column("created_at", DateTime, nullable=False))