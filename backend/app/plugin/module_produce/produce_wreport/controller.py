# -*- coding: utf-8 -*-
import urllib.parse
from typing import Annotated

from fastapi import APIRouter, Body, Depends, File, Path, Query, UploadFile, status
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import ResponseSchema, StreamResponse, SuccessResponse
from app.core.base_schema import AuthSchema, BatchSetAvailable, PageResultSchema, PaginationQueryParam
from app.core.dependencies import AuthPermission, db_getter
from app.core.router_class import OperationLogRoute
from app.utils.common_util import bytes2file_response

from .schema import ProduceWreportCreateSchema, ProduceWreportOutSchema, ProduceWreportQueryParam, ProduceWreportUpdateSchema
from .service import ProduceWreportService

ProduceWreportRouter = APIRouter(route_class=OperationLogRoute, prefix="/produce_wreport", tags=["提报工单模块"])


@ProduceWreportRouter.get("/detail/{id}", summary="获取提报工单详情", response_model=ResponseSchema[ProduceWreportOutSchema])
async def get_obj_detail_controller(
    auth: Annotated[AuthSchema, Depends(AuthPermission(["module_produce:produce_wreport:detail"]))],
    id: Annotated[int, Path(description="提报工单ID")],
    db: Annotated[AsyncSession, Depends(db_getter)],
) -> JSONResponse:
    service = ProduceWreportService(auth, db)
    result_dict = await service.detail(id=id)
    return SuccessResponse(data=result_dict, msg="获取提报工单详情成功")


@ProduceWreportRouter.get("/list", summary="分页查询提报工单", response_model=ResponseSchema[PageResultSchema[ProduceWreportOutSchema]])
async def get_obj_list_controller(
    auth: Annotated[AuthSchema, Depends(AuthPermission(["module_produce:produce_wreport:query"]))],
    page: Annotated[PaginationQueryParam, Depends()],
    search: Annotated[ProduceWreportQueryParam, Query()],
    db: Annotated[AsyncSession, Depends(db_getter)],
) -> JSONResponse:
    service = ProduceWreportService(auth, db)
    result_dict = await service.page(
        page_no=page.page_no,
        page_size=page.page_size,
        search=search,
        order_by=page.order_by,
    )
    return SuccessResponse(data=result_dict, msg="查询提报工单列表成功")


@ProduceWreportRouter.post("/create", status_code=status.HTTP_201_CREATED, summary="创建提报工单", response_model=ResponseSchema[ProduceWreportOutSchema])
async def create_obj_controller(
    auth: Annotated[AuthSchema, Depends(AuthPermission(["module_produce:produce_wreport:create"]))],
    data: Annotated[ProduceWreportCreateSchema, Body(description="创建参数")],
    db: Annotated[AsyncSession, Depends(db_getter)],
) -> JSONResponse:
    service = ProduceWreportService(auth, db)
    result_dict = await service.create(data=data)
    return SuccessResponse(data=result_dict, msg="创建提报工单成功")


@ProduceWreportRouter.put("/update/{id}", summary="修改提报工单", response_model=ResponseSchema[ProduceWreportOutSchema])
async def update_obj_controller(
    auth: Annotated[AuthSchema, Depends(AuthPermission(["module_produce:produce_wreport:update"]))],
    id: Annotated[int, Path(description="提报工单ID")],
    data: Annotated[ProduceWreportUpdateSchema, Body(description="修改参数")],
    db: Annotated[AsyncSession, Depends(db_getter)],
) -> JSONResponse:
    service = ProduceWreportService(auth, db)
    result_dict = await service.update(id=id, data=data)
    return SuccessResponse(data=result_dict, msg="修改提报工单成功")


@ProduceWreportRouter.delete("/delete", summary="删除提报工单", response_model=ResponseSchema[None])
async def delete_obj_controller(
    auth: Annotated[AuthSchema, Depends(AuthPermission(["module_produce:produce_wreport:delete"]))],
    ids: Annotated[list[int], Body(description="ID列表")],
    db: Annotated[AsyncSession, Depends(db_getter)],
) -> JSONResponse:
    service = ProduceWreportService(auth, db)
    await service.delete(ids=ids)
    return SuccessResponse(msg="删除提报工单成功")


@ProduceWreportRouter.patch("/status/batch", summary="批量修改提报工单状态", response_model=ResponseSchema[None])
async def batch_set_available_obj_controller(
    auth: Annotated[AuthSchema, Depends(AuthPermission(["module_produce:produce_wreport:patch"]))],
    data: Annotated[BatchSetAvailable, Body(description="状态设置")],
    db: Annotated[AsyncSession, Depends(db_getter)],
) -> JSONResponse:
    service = ProduceWreportService(auth, db)
    await service.set_available(data=data)
    return SuccessResponse(msg="批量修改提报工单状态成功")


@ProduceWreportRouter.post("/export", summary="导出提报工单")
async def export_obj_list_controller(
    auth: Annotated[AuthSchema, Depends(AuthPermission(["module_produce:produce_wreport:export"]))],
    search: Annotated[ProduceWreportQueryParam, Query()],
    db: Annotated[AsyncSession, Depends(db_getter)],
) -> StreamingResponse:
    service = ProduceWreportService(auth, db)
    result_dict_list = await service.get_list(search=search)
    export_result = ProduceWreportService.batch_export(obj_list=[item.model_dump() for item in result_dict_list])

    return StreamResponse(
        data=bytes2file_response(export_result),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=produce_wreport.xlsx"},
    )


@ProduceWreportRouter.post("/import", summary="导入提报工单", response_model=ResponseSchema[str])
async def import_obj_list_controller(
    file: Annotated[UploadFile, File(description="导入文件")],
    auth: Annotated[AuthSchema, Depends(AuthPermission(["module_produce:produce_wreport:import"]))],
    db: Annotated[AsyncSession, Depends(db_getter)],
) -> JSONResponse:
    service = ProduceWreportService(auth, db)
    batch_import_result = await service.batch_import(file=file, update_support=True)
    return SuccessResponse(data=batch_import_result, msg="导入提报工单成功")


@ProduceWreportRouter.post("/download/template", summary="获取提报工单导入模板", dependencies=[Depends(AuthPermission(["module_produce:produce_wreport:download"]))])
async def export_obj_template_controller() -> StreamingResponse:
    import_template_result = ProduceWreportService.import_template_download()

    return StreamResponse(
        data=bytes2file_response(import_template_result),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={urllib.parse.quote('提报工单导入模板.xlsx')}",
            "Access-Control-Expose-Headers": "Content-Disposition",
        },
    )
