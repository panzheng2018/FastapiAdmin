# -*- coding: utf-8 -*-


from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from app.core.base_schema import BaseSchema, UserBySchema, BaseQueryParam, UserByQueryParam, DateTimeStr

class ProduceWorderCreateSchema(BaseModel):
    """
    工单管理新增模型
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
    status: str = Field(default="0", description='状态 0=待生产 1=生产中 2=已完成 3=已取消 4=已暂停')
    description: str | None = Field(default=None, description='备注/描述')


class ProduceWorderUpdateSchema(BaseModel):
    """
    工单管理更新模型
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
    status: str | None = Field(default=None, description='状态 0=待生产 1=生产中 2=已完成 3=已取消 4=已暂停')
    description: str | None = Field(default=None, description='备注/描述')


class ProduceWorderOutSchema(ProduceWorderCreateSchema, BaseSchema, UserBySchema):
    """
    工单管理响应模型
    """
    model_config = ConfigDict(from_attributes=True)
    craft_name: str | None = Field(default=None, description="工艺名称")
    plan_user_name: str | None = Field(default=None, description="执行用户名称")
    real_user_name: str | None = Field(default=None, description="实际用户名称")
    component_name: str | None = Field(default=None, description="部件名称")


class ProduceWorderQueryParam(BaseQueryParam, UserByQueryParam):
    """工单管理查询参数"""

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
    status: str | None = Field(None, description="状态 0=待生产 1=生产中 2=已完成 3=已取消 4=已暂停", json_schema_extra={"q": "like"})
