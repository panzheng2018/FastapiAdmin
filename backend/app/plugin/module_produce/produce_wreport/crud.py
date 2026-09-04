# -*- coding: utf-8 -*-

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.base_crud import CRUDBase
from app.core.base_schema import AuthSchema
from .model import ProduceWreportModel
from .schema import ProduceWreportCreateSchema, ProduceWreportUpdateSchema


class ProduceWreportCRUD(CRUDBase[ProduceWreportModel, ProduceWreportCreateSchema, ProduceWreportUpdateSchema]):
    """提报工单数据层（复用 produce_worder 表）"""

    def __init__(self, auth: AuthSchema, db: AsyncSession) -> None:
        """
        初始化CRUD数据层

        参数:
        - auth (AuthSchema): 认证信息模型
        - db (AsyncSession): 数据库会话
        """
        super().__init__(model=ProduceWreportModel, auth=auth, db=db)
