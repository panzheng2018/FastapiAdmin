# -*- coding: utf-8 -*-

from sqlalchemy import Text, ForeignKey, String, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base_model import ModelMixin, UserMixin


class ProduceComponentModel(ModelMixin, UserMixin):
    """
    部件信息表
    """
    __tablename__: str = 'produce_component'
    __table_args__: dict[str, str] = {'comment': '部件信息'}
    project_id: Mapped[int | None] = mapped_column(Integer, ForeignKey('produce_project.id', ondelete='CASCADE'), nullable=False, comment='所属项目id')
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment='部件名称')
    code: Mapped[str | None] = mapped_column(String(64), nullable=True, comment='部件编码')
    count: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='数量')
    tmass: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='总重')
    status: Mapped[str] = mapped_column(String(8), nullable=False, comment='是否启用(0:启用 1:禁用)')
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment='备注/描述')

    produce_project = relationship('ProduceProjectModel', back_populates='produce_component_list')
