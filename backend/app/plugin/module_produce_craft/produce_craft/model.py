# -*- coding: utf-8 -*-

from sqlalchemy import Text, String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base_model import ModelMixin, UserMixin


class ProduceCraftModel(ModelMixin, UserMixin):
    """
    工艺管理表
    """
    __tablename__: str = 'produce_craft'
    __table_args__: dict[str, str] = {'comment': '工艺管理'}
    parent_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='父工艺ID')
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment='工艺名称')
    status: Mapped[str] = mapped_column(String(8), nullable=False, comment='是否启用(0:启用 1:禁用)')
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment='备注/描述')

