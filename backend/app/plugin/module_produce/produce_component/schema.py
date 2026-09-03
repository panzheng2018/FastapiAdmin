# -*- coding: utf-8 -*-


from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from app.core.base_schema import BaseSchema, UserBySchema, BaseQueryParam, UserByQueryParam

class ProduceComponentCreateSchema(BaseModel):
    """
    部件管理新增模型
    """
    project_id: int = Field(default=..., description='所属项目id')
    name: str = Field(default=..., description='部件名称')
    code: str | None = Field(default=None, description='部件编码')
    count: int | None = Field(default=None, description='数量')
    tmass: int | None = Field(default=None, description='总重')
    status: str = Field(default="0", description='是否启用(0:启用 1:禁用)')
    description: str | None = Field(default=None, description='备注/描述')


class ProduceComponentUpdateSchema(BaseModel):
    """
    部件管理更新模型
    """
    project_id: int | None = Field(default=None, description='所属项目id')
    name: str | None = Field(default=None, description='部件名称')
    code: str | None = Field(default=None, description='部件编码')
    count: int | None = Field(default=None, description='数量')
    tmass: int | None = Field(default=None, description='总重')
    status: str | None = Field(default=None, description='是否启用(0:启用 1:禁用)')
    description: str | None = Field(default=None, description='备注/描述')


class ProduceComponentOutSchema(ProduceComponentCreateSchema, BaseSchema, UserBySchema):
    """
    部件管理响应模型
    """
    model_config = ConfigDict(from_attributes=True)


class ProduceComponentQueryParam(BaseQueryParam, UserByQueryParam):
    """部件管理查询参数"""

    project_id: int | None = Field(None, description="所属项目id", json_schema_extra={"q": "eq"})
    name: str | None = Field(None, description="部件名称", json_schema_extra={"q": "like"})
    code: str | None = Field(None, description="部件编码", json_schema_extra={"q": "like"})
    count: int | None = Field(None, description="数量", json_schema_extra={"q": "eq"})
    tmass: int | None = Field(None, description="总重", json_schema_extra={"q": "eq"})
    status: str | None = Field(None, description="是否启用(0:启用 1:禁用)", json_schema_extra={"q": "like"})
