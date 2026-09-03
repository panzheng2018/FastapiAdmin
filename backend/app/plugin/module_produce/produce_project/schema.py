# -*- coding: utf-8 -*-

from typing import List

from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from app.core.base_schema import BaseSchema, UserBySchema, BaseQueryParam, UserByQueryParam

class ProduceProjectCreateSchema(BaseModel):
    """
    项目管理新增模型
    """
    name: str = Field(default=..., description='项目名称')
    code: str | None = Field(default=None, description='项目编码')
    no: str | None = Field(default=None, description='项目编号')
    status: str = Field(default="0", description='是否启用(0:启用 1:禁用)')
    description: str | None = Field(default=None, description='备注/描述')


class ProduceProjectUpdateSchema(BaseModel):
    """
    项目管理更新模型
    """
    name: str | None = Field(default=None, description='项目名称')
    code: str | None = Field(default=None, description='项目编码')
    no: str | None = Field(default=None, description='项目编号')
    status: str | None = Field(default=None, description='是否启用(0:启用 1:禁用)')
    description: str | None = Field(default=None, description='备注/描述')


class ProduceProjectOutSchema(ProduceProjectCreateSchema, BaseSchema, UserBySchema):
    """
    项目管理响应模型
    """
    model_config = ConfigDict(from_attributes=True)


class ProduceProjectQueryParam(BaseQueryParam, UserByQueryParam):
    """项目管理查询参数"""

    name: str | None = Field(None, description="项目名称", json_schema_extra={"q": "like"})
    code: str | None = Field(None, description="项目编码", json_schema_extra={"q": "like"})
    no: str | None = Field(None, description="项目编号", json_schema_extra={"q": "like"})
    status: str | None = Field(None, description="是否启用(0:启用 1:禁用)", json_schema_extra={"q": "like"})
