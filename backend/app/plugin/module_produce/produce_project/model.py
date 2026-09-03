# -*- coding: utf-8 -*-

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base_model import ModelMy


class ProduceProjectModel(ModelMy):
    """
    项目管理表
    """
    __tablename__: str = 'produce_project'
    __table_args__: dict[str, str] = {'comment': '项目管理'}
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment='项目名称')
    code: Mapped[str | None] = mapped_column(String(64), nullable=True, comment='项目编码')
    no: Mapped[str | None] = mapped_column(String(64), nullable=True, comment='项目编号')

