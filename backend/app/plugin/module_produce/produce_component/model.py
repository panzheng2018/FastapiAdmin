# -*- coding: utf-8 -*-

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base_model import ModelMy


class ProduceComponentModel(ModelMy):
    """
    部件管理表
    """
    __tablename__: str = 'produce_component'
    __table_args__: dict[str, str] = {'comment': '部件管理'}
    project_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("produce_project.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        comment='所属项目id',
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment='部件名称')
    code: Mapped[str | None] = mapped_column(String(64), nullable=True, comment='部件编码')
    count: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='数量')
    tmass: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='总重')


