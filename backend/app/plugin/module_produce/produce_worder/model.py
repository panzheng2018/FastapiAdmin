# -*- coding: utf-8 -*-

from datetime import datetime
from sqlalchemy import Integer, DateTime, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base_model import ModelMy
from app.api.v1.module_system.user.model import UserModel
from app.plugin.module_produce.produce_craft.model import ProduceCraftModel
from app.plugin.module_produce.produce_component.model import ProduceComponentModel


class ProduceWorderModel(ModelMy):
    """
    工单管理表
    """
    __tablename__: str = 'produce_worder'
    __table_args__: dict[str, str] = {'comment': '工单管理'}
    no: Mapped[str] = mapped_column(String(32), nullable=False, comment='单号')
    component_id: Mapped[int] = mapped_column(ForeignKey("produce_component.id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False, comment='部件id')
    craft_id: Mapped[int] = mapped_column(ForeignKey("produce_craft.id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False, comment='工艺id')
    man_hour: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment='工时')
    plan_count: Mapped[int] = mapped_column(Integer, nullable=False, comment='数量')
    real_count: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None, comment='实际数量')
    plan_end_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment='完工时间')
    real_end_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment='实际完工时间')
    plan_user_id: Mapped[int] = mapped_column(ForeignKey("sys_user.id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False, comment='执行用户')
    real_user_id: Mapped[int | None] = mapped_column(ForeignKey("sys_user.id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=True, comment='实际执行用户')

    component: Mapped["ProduceComponentModel | None"] = relationship("ProduceComponentModel", foreign_keys=[component_id])
    craft: Mapped["ProduceCraftModel | None"] = relationship("ProduceCraftModel", foreign_keys=[craft_id])
    plan_user: Mapped["UserModel | None"] = relationship("UserModel", foreign_keys=[plan_user_id])
    real_user: Mapped["UserModel | None"] = relationship("UserModel", foreign_keys=[real_user_id])

