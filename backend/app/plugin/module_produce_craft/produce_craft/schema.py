# -*- coding: utf-8 -*-


from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from app.core.base_schema import BaseSchema, UserBySchema, BaseQueryParam, UserByQueryParam

class ProduceCraftCreateSchema(BaseModel):
    """
    工艺管理新增模型
    """
    parent_id: int | None = Field(default=None, description='父工艺ID')
    name: str = Field(default=..., description='工艺名称')
    status: str = Field(default="0", description='是否启用(0:启用 1:禁用)')
    description: str | None = Field(default=None, description='备注/描述')


class ProduceCraftUpdateSchema(BaseModel):
    """
    工艺管理更新模型
    """
    parent_id: int | None = Field(default=None, description='父工艺ID')
    name: str | None = Field(default=None, description='工艺名称')
    status: str | None = Field(default=None, description='是否启用(0:启用 1:禁用)')
    description: str | None = Field(default=None, description='备注/描述')


class ProduceCraftOutSchema(ProduceCraftCreateSchema, BaseSchema, UserBySchema):
    """
    工艺管理响应模型
    """
    model_config = ConfigDict(from_attributes=True)


class ProduceCraftQueryParam(BaseQueryParam, UserByQueryParam):
    """工艺管理查询参数"""

    parent_id: int | None = Field(None, description="父工艺ID", json_schema_extra={"q": "eq"})
    name: str | None = Field(None, description="工艺名称", json_schema_extra={"q": "like"})
    status: str | None = Field(None, description="是否启用(0:启用 1:禁用)", json_schema_extra={"q": "like"})
