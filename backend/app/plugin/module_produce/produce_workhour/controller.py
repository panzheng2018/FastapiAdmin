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

from .schema import ProduceWorkhourCreateSchema, ProduceWorkhourOutSchema, ProduceWorkhourQueryParam, ProduceWorkhourUpdateSchema
from .service import ProduceWorkhourService

ProduceWorkhourRouter = APIRouter(route_class=OperationLogRoute, prefix="/produce_workhour", tags=["工时管理模块"])


@ProduceWorkhourRouter.get("/detail/{id}", summary="获取工时管理详情", response_model=ResponseSchema[ProduceWorkhourOutSchema])
async def get_obj_detail_controller(
    auth: Annotated[AuthSchema, Depends(AuthPermission(["module_produce:produce_workhour:detail"]))],
    id: Annotated[int, Path(description="工时管理ID")],
    db: Annotated[AsyncSession, Depends(db_getter)],
) -> JSONResponse:
    service = ProduceWorkhourService(auth, db)
    result_dict = await service.detail(id=id)
    return SuccessResponse(data=result_dict, msg="获取工时管理详情成功")


@ProduceWorkhourRouter.get("/list", summary="分页查询工时管理", response_model=ResponseSchema[PageResultSchema[ProduceWorkhourOutSchema]])
async def get_obj_list_controller(
    auth: Annotated[AuthSchema, Depends(AuthPermission(["module_produce:produce_workhour:query"]))],
    page: Annotated[PaginationQueryParam, Depends()],
    search: Annotated[ProduceWorkhourQueryParam, Query()],
    db: Annotated[AsyncSession, Depends(db_getter)],
) -> JSONResponse:
    service = ProduceWorkhourService(auth, db)
    result_dict = await service.page(
        page_no=page.page_no,
        page_size=page.page_size,
        search=search,
        order_by=page.order_by,
    )
    return SuccessResponse(data=result_dict, msg="查询工时管理列表成功")


@ProduceWorkhourRouter.post("/create", status_code=status.HTTP_201_CREATED, summary="创建工时管理", response_model=ResponseSchema[ProduceWorkhourOutSchema])
async def create_obj_controller(
    auth: Annotated[AuthSchema, Depends(AuthPermission(["module_produce:produce_workhour:create"]))],
    data: Annotated[ProduceWorkhourCreateSchema, Body(description="创建参数")],
    db: Annotated[AsyncSession, Depends(db_getter)],
) -> JSONResponse:
    service = ProduceWorkhourService(auth, db)
    result_dict = await service.create(data=data)
    return SuccessResponse(data=result_dict, msg="创建工时管理成功")


@ProduceWorkhourRouter.put("/update/{id}", summary="修改工时管理", response_model=ResponseSchema[ProduceWorkhourOutSchema])
async def update_obj_controller(
    auth: Annotated[AuthSchema, Depends(AuthPermission(["module_produce:produce_workhour:update"]))],
    id: Annotated[int, Path(description="工时管理ID")],
    data: Annotated[ProduceWorkhourUpdateSchema, Body(description="修改参数")],
    db: Annotated[AsyncSession, Depends(db_getter)],
) -> JSONResponse:
    service = ProduceWorkhourService(auth, db)
    result_dict = await service.update(id=id, data=data)
    return SuccessResponse(data=result_dict, msg="修改工时管理成功")


@ProduceWorkhourRouter.delete("/delete", summary="删除工时管理", response_model=ResponseSchema[None])
async def delete_obj_controller(
    auth: Annotated[AuthSchema, Depends(AuthPermission(["module_produce:produce_workhour:delete"]))],
    ids: Annotated[list[int], Body(description="ID列表")],
    db: Annotated[AsyncSession, Depends(db_getter)],
) -> JSONResponse:
    service = ProduceWorkhourService(auth, db)
    await service.delete(ids=ids)
    return SuccessResponse(msg="删除工时管理成功")


@ProduceWorkhourRouter.patch("/status/batch", summary="批量修改工时管理状态", response_model=ResponseSchema[None])
async def batch_set_available_obj_controller(
    auth: Annotated[AuthSchema, Depends(AuthPermission(["module_produce:produce_workhour:patch"]))],
    data: Annotated[BatchSetAvailable, Body(description="状态设置")],
    db: Annotated[AsyncSession, Depends(db_getter)],
) -> JSONResponse:
    service = ProduceWorkhourService(auth, db)
    await service.set_available(data=data)
    return SuccessResponse(msg="批量修改工时管理状态成功")


@ProduceWorkhourRouter.post("/export", summary="导出工时管理")
async def export_obj_list_controller(
    auth: Annotated[AuthSchema, Depends(AuthPermission(["module_produce:produce_workhour:export"]))],
    search: Annotated[ProduceWorkhourQueryParam, Query()],
    db: Annotated[AsyncSession, Depends(db_getter)],
) -> StreamingResponse:
    service = ProduceWorkhourService(auth, db)
    result_dict_list = await service.get_list(search=search)
    export_result = ProduceWorkhourService.batch_export(obj_list=[item.model_dump() for item in result_dict_list])

    return StreamResponse(
        data=bytes2file_response(export_result),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=produce_workhour.xlsx"},
    )


@ProduceWorkhourRouter.post("/import", summary="导入工时管理", response_model=ResponseSchema[str])
async def import_obj_list_controller(
    file: Annotated[UploadFile, File(description="导入文件")],
    auth: Annotated[AuthSchema, Depends(AuthPermission(["module_produce:produce_workhour:import"]))],
    db: Annotated[AsyncSession, Depends(db_getter)],
) -> JSONResponse:
    service = ProduceWorkhourService(auth, db)
    batch_import_result = await service.batch_import(file=file, update_support=True)
    return SuccessResponse(data=batch_import_result, msg="导入工时管理成功")


@ProduceWorkhourRouter.post("/download/template", summary="获取工时管理导入模板", dependencies=[Depends(AuthPermission(["module_produce:produce_workhour:download"]))])
async def export_obj_template_controller() -> StreamingResponse:
    import_template_result = ProduceWorkhourService.import_template_download()

    return StreamResponse(
        data=bytes2file_response(import_template_result),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={urllib.parse.quote('工时管理导入模板.xlsx')}",
            "Access-Control-Expose-Headers": "Content-Disposition",
        },
    )
