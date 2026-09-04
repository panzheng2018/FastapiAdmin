# -*- coding: utf-8 -*-

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.core.base_schema import BaseSchema, UserBySchema, BaseQueryParam, UserByQueryParam, DateTimeStr


class ProduceWreportCreateSchema(BaseModel):
    """
    提报工单新增模型
    """
    no: str = Field(default=..., description='单号')
    component_id: int = Field(default=..., description='部件id')
    craft_id: int = Field(default=..., description='工艺id')
    man_hour: int = Field(default=0, description='工时')
    plan_count: int = Field(default=1, description='数量')
    real_count: int | None = Field(default=None, description='实际数量')
    plan_end_time: DateTimeStr | None = Field(default=None, description='完工时间')
    real_end_time: DateTimeStr | None = Field(default=None, description='实际时间')
    plan_user_id: int = Field(default=..., description='执行用户')
    real_user_id: int | None = Field(default=None, description='实际用户')
    status: str = Field(default="2", description='状态 0=启用 1=禁用 2=待生产 3=生产中 4=已完成 5=已取消 6=已暂停')
    description: str | None = Field(default=None, description='备注/描述')


class ProduceWreportUpdateSchema(BaseModel):
    """
    提报工单更新模型
    """
    no: str | None = Field(default=None, description='单号')
    component_id: int | None = Field(default=None, description='部件id')
    craft_id: int | None = Field(default=None, description='工艺id')
    man_hour: int | None = Field(default=None, description='工时')
    plan_count: int | None = Field(default=None, description='数量')
    real_count: int | None = Field(default=None, description='实际数量')
    plan_end_time: DateTimeStr | None = Field(default=None, description='完工时间')
    real_end_time: DateTimeStr | None = Field(default=None, description='实际时间')
    plan_user_id: int | None = Field(default=None, description='执行用户')
    real_user_id: int | None = Field(default=None, description='实际用户')
    status: str | None = Field(default=None, description='状态 0=启用 1=禁用 2=待生产 3=生产中 4=已完成 5=已取消 6=已暂停')
    description: str | None = Field(default=None, description='备注/描述')


class ProduceWreportOutSchema(ProduceWreportCreateSchema, BaseSchema, UserBySchema):
    """
    提报工单响应模型
    """
    model_config = ConfigDict(from_attributes=True)
    craft_name: str | None = Field(default=None, description="工艺名称")
    plan_user_name: str | None = Field(default=None, description="执行用户名称")
    real_user_name: str | None = Field(default=None, description="实际用户名称")
    project_id: int | None = Field(default=None, description="所属项目ID")
    project_name: str | None = Field(default=None, description="所属项目名称")
    component_name: str | None = Field(default=None, description="部件名称")


class ProduceWreportQueryParam(BaseQueryParam, UserByQueryParam):
    """提报工单查询参数"""

    no: str | None = Field(None, description="单号", json_schema_extra={"q": "like"})
    component_id: int | None = Field(None, description="部件id", json_schema_extra={"q": "eq"})
    craft_id: int | None = Field(None, description="工艺id", json_schema_extra={"q": "eq"})
    man_hour: int | None = Field(None, description="工时", json_schema_extra={"q": "eq"})
    plan_count: int | None = Field(None, description="数量", json_schema_extra={"q": "eq"})
    real_count: int | None = Field(None, description="实际数量", json_schema_extra={"q": "eq"})
    plan_end_time: datetime | None = Field(None, description="计划完工时间", json_schema_extra={"q": "eq"})
    real_end_time: datetime | None = Field(None, description="实际时间", json_schema_extra={"q": "eq"})
    plan_user_id: int | None = Field(None, description="计划执行用户", json_schema_extra={"q": "eq"})
    real_user_id: int | None = Field(None, description="实际用户", json_schema_extra={"q": "eq"})
    status: str | None = Field(None, description="状态 0=启用 1=禁用 2=待生产 3=生产中 4=已完成 5=已取消 6=已暂停", json_schema_extra={"q": "like"})
