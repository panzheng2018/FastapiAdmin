# -*- coding: utf-8 -*-

from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base_model import ModelMy
from app.api.v1.module_system.position.model import PositionModel


class ProduceCraftModel(ModelMy):
    """
    工艺管理表
    """
    __tablename__: str = 'produce_craft'
    __table_args__: dict[str, str] = {'comment': '工艺管理'}
    parent_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("produce_craft.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=True,
        comment='父工艺ID',
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment='工艺名称')
    position_id: Mapped[int | None] = mapped_column(ForeignKey("sys_position.id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=True, comment='关联岗位ID')

    parent: Mapped["ProduceCraftModel | None"] = relationship(
        "ProduceCraftModel",
        remote_side="ProduceCraftModel.id",
        foreign_keys=[parent_id],
        uselist=False,
    )
    position: Mapped["PositionModel | None"] = relationship("PositionModel", foreign_keys=[position_id])


