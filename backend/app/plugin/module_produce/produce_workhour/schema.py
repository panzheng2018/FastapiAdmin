# -*- coding: utf-8 -*-

"""
工时管理模型模式
移除“完工时间(plan_end_time)”、“执行用户(plan_user_id)”、“实际时间(real_end_time)”与“实际用户(real_user_id)”字段
"""
from pydantic import BaseModel, ConfigDict, Field
from app.core.base_schema import BaseSchema, UserBySchema, BaseQueryParam, UserByQueryParam


class ProduceWorkhourCreateSchema(BaseModel):
    """工时管理新增模型（无完工时间、执行用户、实际时间、实际用户）"""
    no: str = Field(default=..., description='单号')
    component_id: int = Field(default=..., description='部件id')
    craft_id: int = Field(default=..., description='工艺id')
    man_hour: int = Field(default=0, description='工时')
    plan_count: int = Field(default=1, description='数量')
    real_count: int | None = Field(default=None, description='实际数量')
    status: str = Field(default="0", description='状态 0=启用 1=禁用 2=待生产 3=生产中 4=已完成 5=已取消 6=已暂停')
    description: str | None = Field(default=None, description='备注/描述')


class ProduceWorkhourUpdateSchema(BaseModel):
    """工时管理更新模型（无完工时间、执行用户、实际时间、实际用户）"""
    no: str | None = Field(default=None, description='单号')
    component_id: int | None = Field(default=None, description='部件id')
    craft_id: int | None = Field(default=None, description='工艺id')
    man_hour: int | None = Field(default=None, description='工时')
    plan_count: int | None = Field(default=None, description='数量')
    real_count: int | None = Field(default=None, description='实际数量')
    status: str | None = Field(default=None, description='状态 0=启用 1=禁用 2=待生产 3=生产中 4=已完成 5=已取消 6=已暂停')
    description: str | None = Field(default=None, description='备注/描述')


class ProduceWorkhourOutSchema(ProduceWorkhourCreateSchema, BaseSchema, UserBySchema):
    """工时管理响应模型（无完工时间、执行用户、实际时间、实际用户）"""
    model_config = ConfigDict(from_attributes=True)
    craft_name: str | None = Field(default=None, description="工艺名称")
    project_id: int | None = Field(default=None, description="所属项目ID")
    project_name: str | None = Field(default=None, description="所属项目名称")
    component_name: str | None = Field(default=None, description="部件名称")


class ProduceWorkhourQueryParam(BaseQueryParam, UserByQueryParam):
    """工时管理查询参数（无完工时间、执行用户、实际时间、实际用户）"""
    no: str | None = Field(None, description="单号", json_schema_extra={"q": "like"})
    component_id: int | None = Field(None, description="部件id", json_schema_extra={"q": "eq"})
    craft_id: int | None = Field(None, description="工艺id", json_schema_extra={"q": "eq"})
    man_hour: int | None = Field(None, description="工时", json_schema_extra={"q": "eq"})
    plan_count: int | None = Field(None, description="数量", json_schema_extra={"q": "eq"})
    real_count: int | None = Field(None, description="实际数量", json_schema_extra={"q": "eq"})
    status: str | None = Field(None, description="状态 0=启用 1=禁用 2=待生产 3=生产中 4=已完成 5=已取消 6=已暂停", json_schema_extra={"q": "like"})
