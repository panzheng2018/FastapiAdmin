# -*- coding: utf-8 -*-

from datetime import datetime
from sqlalchemy import DateTime, Text, String, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base_model import ModelMixin, UserMixin
from ..produce_component.model import ProduceComponentModel


class ProduceProjectModel(ModelMixin, UserMixin):
    """
    项目管理表
    """
    __tablename__: str = 'produce_project'
    __table_args__: dict[str, str] = {'comment': '项目管理'}
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment='项目名称')
    code: Mapped[str | None] = mapped_column(String(64), nullable=True, comment='项目编码')
    no: Mapped[str | None] = mapped_column(String(64), nullable=True, comment='项目编号')
    status: Mapped[str] = mapped_column(String(8), nullable=False, comment='是否启用(0:启用 1:禁用)')
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment='备注/描述')

    produce_component_list = relationship('ProduceComponentModel', back_populates='produce_project')
