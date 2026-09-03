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

from .schema import ProduceCraftCreateSchema, ProduceCraftOutSchema, ProduceCraftQueryParam, ProduceCraftUpdateSchema
from .service import ProduceCraftService

ProduceCraftRouter = APIRouter(route_class=OperationLogRoute, prefix="/produce_craft", tags=["工艺管理模块"])


@ProduceCraftRouter.get("/detail/{id}", summary="获取工艺管理详情", response_model=ResponseSchema[ProduceCraftOutSchema])
async def get_obj_detail_controller(
    auth: Annotated[AuthSchema, Depends(AuthPermission(["module_produce:produce_craft:detail"]))],
    id: Annotated[int, Path(description="工艺管理ID")],
    db: Annotated[AsyncSession, Depends(db_getter)],
) -> JSONResponse:
    service = ProduceCraftService(auth, db)
    result_dict = await service.detail(id=id)
    return SuccessResponse(data=result_dict, msg="获取工艺管理详情成功")


@ProduceCraftRouter.get("/list", summary="分页查询工艺管理", response_model=ResponseSchema[PageResultSchema[ProduceCraftOutSchema]])
async def get_obj_list_controller(
    auth: Annotated[AuthSchema, Depends(AuthPermission(["module_produce:produce_craft:query"]))],
    page: Annotated[PaginationQueryParam, Depends()],
    search: Annotated[ProduceCraftQueryParam, Query()],
    db: Annotated[AsyncSession, Depends(db_getter)],
) -> JSONResponse:
    service = ProduceCraftService(auth, db)
    result_dict = await service.page(
        page_no=page.page_no,
        page_size=page.page_size,
        search=search,
        order_by=page.order_by,
    )
    return SuccessResponse(data=result_dict, msg="查询工艺管理列表成功")


@ProduceCraftRouter.post("/create", status_code=status.HTTP_201_CREATED, summary="创建工艺管理", response_model=ResponseSchema[ProduceCraftOutSchema])
async def create_obj_controller(
    auth: Annotated[AuthSchema, Depends(AuthPermission(["module_produce:produce_craft:create"]))],
    data: Annotated[ProduceCraftCreateSchema, Body(description="创建参数")],
    db: Annotated[AsyncSession, Depends(db_getter)],
) -> JSONResponse:
    service = ProduceCraftService(auth, db)
    result_dict = await service.create(data=data)
    return SuccessResponse(data=result_dict, msg="创建工艺管理成功")


@ProduceCraftRouter.put("/update/{id}", summary="修改工艺管理", response_model=ResponseSchema[ProduceCraftOutSchema])
async def update_obj_controller(
    auth: Annotated[AuthSchema, Depends(AuthPermission(["module_produce:produce_craft:update"]))],
    id: Annotated[int, Path(description="工艺管理ID")],
    data: Annotated[ProduceCraftUpdateSchema, Body(description="修改参数")],
    db: Annotated[AsyncSession, Depends(db_getter)],
) -> JSONResponse:
    service = ProduceCraftService(auth, db)
    result_dict = await service.update(id=id, data=data)
    return SuccessResponse(data=result_dict, msg="修改工艺管理成功")


@ProduceCraftRouter.delete("/delete", summary="删除工艺管理", response_model=ResponseSchema[None])
async def delete_obj_controller(
    auth: Annotated[AuthSchema, Depends(AuthPermission(["module_produce:produce_craft:delete"]))],
    ids: Annotated[list[int], Body(description="ID列表")],
    db: Annotated[AsyncSession, Depends(db_getter)],
) -> JSONResponse:
    service = ProduceCraftService(auth, db)
    await service.delete(ids=ids)
    return SuccessResponse(msg="删除工艺管理成功")


@ProduceCraftRouter.patch("/status/batch", summary="批量修改工艺管理状态", response_model=ResponseSchema[None])
async def batch_set_available_obj_controller(
    auth: Annotated[AuthSchema, Depends(AuthPermission(["module_produce:produce_craft:patch"]))],
    data: Annotated[BatchSetAvailable, Body(description="状态设置")],
    db: Annotated[AsyncSession, Depends(db_getter)],
) -> JSONResponse:
    service = ProduceCraftService(auth, db)
    await service.set_available(data=data)
    return SuccessResponse(msg="批量修改工艺管理状态成功")


@ProduceCraftRouter.post("/export", summary="导出工艺管理")
async def export_obj_list_controller(
    auth: Annotated[AuthSchema, Depends(AuthPermission(["module_produce:produce_craft:export"]))],
    search: Annotated[ProduceCraftQueryParam, Query()],
    db: Annotated[AsyncSession, Depends(db_getter)],
) -> StreamingResponse:
    service = ProduceCraftService(auth, db)
    result_dict_list = await service.get_list(search=search)
    export_result = ProduceCraftService.batch_export(obj_list=[item.model_dump() for item in result_dict_list])

    return StreamResponse(
        data=bytes2file_response(export_result),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=produce_craft.xlsx"},
    )


@ProduceCraftRouter.post("/import", summary="导入工艺管理", response_model=ResponseSchema[str])
async def import_obj_list_controller(
    file: Annotated[UploadFile, File(description="导入文件")],
    auth: Annotated[AuthSchema, Depends(AuthPermission(["module_produce:produce_craft:import"]))],
    db: Annotated[AsyncSession, Depends(db_getter)],
) -> JSONResponse:
    service = ProduceCraftService(auth, db)
    batch_import_result = await service.batch_import(file=file, update_support=True)
    return SuccessResponse(data=batch_import_result, msg="导入工艺管理成功")


@ProduceCraftRouter.post("/download/template", summary="获取工艺管理导入模板", dependencies=[Depends(AuthPermission(["module_produce:produce_craft:download"]))])
async def export_obj_template_controller() -> StreamingResponse:
    import_template_result = ProduceCraftService.import_template_download()

    return StreamResponse(
        data=bytes2file_response(import_template_result),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={urllib.parse.quote('工艺管理导入模板.xlsx')}",
            "Access-Control-Expose-Headers": "Content-Disposition",
        },
    )
