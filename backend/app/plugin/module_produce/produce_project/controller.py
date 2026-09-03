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

from .schema import ProduceProjectCreateSchema, ProduceProjectOutSchema, ProduceProjectQueryParam, ProduceProjectUpdateSchema
from .service import ProduceProjectService

ProduceProjectRouter = APIRouter(route_class=OperationLogRoute, prefix="/produce_project", tags=["项目管理模块"])


@ProduceProjectRouter.get("/detail/{id}", summary="获取项目管理详情", response_model=ResponseSchema[ProduceProjectOutSchema])
async def get_obj_detail_controller(
    auth: Annotated[AuthSchema, Depends(AuthPermission(["module_produce:produce_project:detail"]))],
    id: Annotated[int, Path(description="项目管理ID")],
    db: Annotated[AsyncSession, Depends(db_getter)],
) -> JSONResponse:
    service = ProduceProjectService(auth, db)
    result_dict = await service.detail(id=id)
    return SuccessResponse(data=result_dict, msg="获取项目管理详情成功")


@ProduceProjectRouter.get("/list", summary="分页查询项目管理", response_model=ResponseSchema[PageResultSchema[ProduceProjectOutSchema]])
async def get_obj_list_controller(
    auth: Annotated[AuthSchema, Depends(AuthPermission(["module_produce:produce_project:query"]))],
    page: Annotated[PaginationQueryParam, Depends()],
    search: Annotated[ProduceProjectQueryParam, Query()],
    db: Annotated[AsyncSession, Depends(db_getter)],
) -> JSONResponse:
    service = ProduceProjectService(auth, db)
    result_dict = await service.page(
        page_no=page.page_no,
        page_size=page.page_size,
        search=search,
        order_by=page.order_by,
    )
    return SuccessResponse(data=result_dict, msg="查询项目管理列表成功")


@ProduceProjectRouter.post("/create", status_code=status.HTTP_201_CREATED, summary="创建项目管理", response_model=ResponseSchema[ProduceProjectOutSchema])
async def create_obj_controller(
    auth: Annotated[AuthSchema, Depends(AuthPermission(["module_produce:produce_project:create"]))],
    data: Annotated[ProduceProjectCreateSchema, Body(description="创建参数")],
    db: Annotated[AsyncSession, Depends(db_getter)],
) -> JSONResponse:
    service = ProduceProjectService(auth, db)
    result_dict = await service.create(data=data)
    return SuccessResponse(data=result_dict, msg="创建项目管理成功")


@ProduceProjectRouter.put("/update/{id}", summary="修改项目管理", response_model=ResponseSchema[ProduceProjectOutSchema])
async def update_obj_controller(
    auth: Annotated[AuthSchema, Depends(AuthPermission(["module_produce:produce_project:update"]))],
    id: Annotated[int, Path(description="项目管理ID")],
    data: Annotated[ProduceProjectUpdateSchema, Body(description="修改参数")],
    db: Annotated[AsyncSession, Depends(db_getter)],
) -> JSONResponse:
    service = ProduceProjectService(auth, db)
    result_dict = await service.update(id=id, data=data)
    return SuccessResponse(data=result_dict, msg="修改项目管理成功")


@ProduceProjectRouter.delete("/delete", summary="删除项目管理", response_model=ResponseSchema[None])
async def delete_obj_controller(
    auth: Annotated[AuthSchema, Depends(AuthPermission(["module_produce:produce_project:delete"]))],
    ids: Annotated[list[int], Body(description="ID列表")],
    db: Annotated[AsyncSession, Depends(db_getter)],
) -> JSONResponse:
    service = ProduceProjectService(auth, db)
    await service.delete(ids=ids)
    return SuccessResponse(msg="删除项目管理成功")


@ProduceProjectRouter.patch("/status/batch", summary="批量修改项目管理状态", response_model=ResponseSchema[None])
async def batch_set_available_obj_controller(
    auth: Annotated[AuthSchema, Depends(AuthPermission(["module_produce:produce_project:patch"]))],
    data: Annotated[BatchSetAvailable, Body(description="状态设置")],
    db: Annotated[AsyncSession, Depends(db_getter)],
) -> JSONResponse:
    service = ProduceProjectService(auth, db)
    await service.set_available(data=data)
    return SuccessResponse(msg="批量修改项目管理状态成功")


@ProduceProjectRouter.post("/export", summary="导出项目管理")
async def export_obj_list_controller(
    auth: Annotated[AuthSchema, Depends(AuthPermission(["module_produce:produce_project:export"]))],
    search: Annotated[ProduceProjectQueryParam, Query()],
    db: Annotated[AsyncSession, Depends(db_getter)],
) -> StreamingResponse:
    service = ProduceProjectService(auth, db)
    result_dict_list = await service.get_list(search=search)
    export_result = ProduceProjectService.batch_export(obj_list=[item.model_dump() for item in result_dict_list])

    return StreamResponse(
        data=bytes2file_response(export_result),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=produce_project.xlsx"},
    )


@ProduceProjectRouter.post("/import", summary="导入项目管理", response_model=ResponseSchema[str])
async def import_obj_list_controller(
    file: Annotated[UploadFile, File(description="导入文件")],
    auth: Annotated[AuthSchema, Depends(AuthPermission(["module_produce:produce_project:import"]))],
    db: Annotated[AsyncSession, Depends(db_getter)],
) -> JSONResponse:
    service = ProduceProjectService(auth, db)
    batch_import_result = await service.batch_import(file=file, update_support=True)
    return SuccessResponse(data=batch_import_result, msg="导入项目管理成功")


@ProduceProjectRouter.post("/download/template", summary="获取项目管理导入模板", dependencies=[Depends(AuthPermission(["module_produce:produce_project:download"]))])
async def export_obj_template_controller() -> StreamingResponse:
    import_template_result = ProduceProjectService.import_template_download()

    return StreamResponse(
        data=bytes2file_response(import_template_result),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={urllib.parse.quote('项目管理导入模板.xlsx')}",
            "Access-Control-Expose-Headers": "Content-Disposition",
        },
    )
