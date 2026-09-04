# -*- coding: utf-8 -*-

"""
工时管理模型模式
工时管理与工单管理使用相同的参数与响应规范
"""
from app.plugin.module_produce.produce_worder.schema import (
    ProduceWorderCreateSchema,
    ProduceWorderUpdateSchema,
    ProduceWorderOutSchema,
    ProduceWorderQueryParam,
)

ProduceWorkhourCreateSchema = ProduceWorderCreateSchema
ProduceWorkhourUpdateSchema = ProduceWorderUpdateSchema
ProduceWorkhourOutSchema = ProduceWorderOutSchema
ProduceWorkhourQueryParam = ProduceWorderQueryParam
