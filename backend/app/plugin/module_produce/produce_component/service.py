# -*- coding: utf-8 -*-

from typing import Any

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.base_schema import AuthSchema, BatchSetAvailable, PageResultSchema
from app.core.exceptions import CustomException
from app.core.logger import logger
from app.plugin.module_produce.produce_project.model import ProduceProjectModel
from app.utils.common_util import search_to_dict
from app.utils.excel_util import ExcelUtil

from .crud import ProduceComponentCRUD
from .schema import (
    ProduceComponentCreateSchema,
    ProduceComponentOutSchema,
    ProduceComponentQueryParam,
    ProduceComponentUpdateSchema,
)


class ProduceComponentService:
    """部件管理模块服务层"""

    def __init__(self, auth: AuthSchema, db: AsyncSession) -> None:
        self.auth = auth
        self.db = db

    async def detail(self, id: int) -> ProduceComponentOutSchema:
        obj = await ProduceComponentCRUD(self.auth, self.db).get(id=id, preload=["project"])
        if not obj:
            raise CustomException(msg="该数据不存在")
        result = ProduceComponentOutSchema.model_validate(obj)
        if getattr(obj, "project", None):
            result.project_name = obj.project.name
        return result

    async def get_list(
        self,
        search: ProduceComponentQueryParam | None = None,
        order_by: list[dict[str, str]] | None = None,
    ) -> list[ProduceComponentOutSchema]:
        search_dict = search_to_dict(search)
        if search and search.project_name:
            search_dict.pop("project_name", None)
            matching_projects = (await self.db.execute(
                select(ProduceProjectModel.id).where(ProduceProjectModel.name.like(f"%{search.project_name}%"))
            )).scalars().all()
            search_dict["project_id"] = ("in", matching_projects)
        obj_list = await ProduceComponentCRUD(self.auth, self.db).get_list(
            search=search_dict,
            order_by=order_by,
            preload=["project"],
        )
        result = []
        for obj in obj_list:
            item = ProduceComponentOutSchema.model_validate(obj)
            if getattr(obj, "project", None):
                item.project_name = obj.project.name
            result.append(item)
        return result

    async def page(
        self,
        page_no: int,
        page_size: int,
        search: ProduceComponentQueryParam | None = None,
        order_by: list[dict[str, str]] | None = None,
    ) -> PageResultSchema[ProduceComponentOutSchema]:
        offset = (page_no - 1) * page_size
        search_dict = search_to_dict(search, {})
        if search and search.project_name:
            search_dict.pop("project_name", None)
            matching_projects = (await self.db.execute(
                select(ProduceProjectModel.id).where(ProduceProjectModel.name.like(f"%{search.project_name}%"))
            )).scalars().all()
            search_dict["project_id"] = ("in", matching_projects)
        page_result = await ProduceComponentCRUD(self.auth, self.db).page(
            offset=offset,
            limit=page_size,
            order_by=order_by or [{"id": "asc"}],
            search=search_dict,
            preload=["project"],
        )
        items: list[ProduceComponentOutSchema] = []
        for obj in page_result.items:
            item = ProduceComponentOutSchema.model_validate(obj)
            if getattr(obj, "project", None):
                item.project_name = obj.project.name
            items.append(item)
        page_result.items = items
        return page_result

    async def create(self, data: ProduceComponentCreateSchema) -> ProduceComponentOutSchema:
        exist_name = await ProduceComponentCRUD(self.auth, self.db).get(name=data.name, project_id=data.project_id)
        if exist_name:
            raise CustomException(msg="创建失败，该项目下部件名称已存在")
        obj = await ProduceComponentCRUD(self.auth, self.db).create(data=data)
        result = ProduceComponentOutSchema.model_validate(obj)
        project = await self.db.get(ProduceProjectModel, data.project_id)
        if project:
            result.project_name = project.name
        return result

    async def update(self, id: int, data: ProduceComponentUpdateSchema) -> ProduceComponentOutSchema:
        obj = await ProduceComponentCRUD(self.auth, self.db).get(id=id)
        if not obj:
            raise CustomException(msg="更新失败，该数据不存在")

        target_project_id = data.project_id or obj.project_id
        target_name = data.name or obj.name
        if target_name and target_project_id:
            exist_name = await ProduceComponentCRUD(self.auth, self.db).get(name=target_name, project_id=target_project_id)
            if exist_name and exist_name.id != id:
                raise CustomException(msg="更新失败，该项目下部件名称重复")

        obj = await ProduceComponentCRUD(self.auth, self.db).update(id=id, data=data)
        result = ProduceComponentOutSchema.model_validate(obj)
        if target_project_id:
            project = await self.db.get(ProduceProjectModel, target_project_id)
            if project:
                result.project_name = project.name
        return result

    async def delete(self, ids: list[int]) -> None:
        if not ids:
            raise CustomException(msg="删除失败，删除对象不能为空")
        objs = await ProduceComponentCRUD(self.auth, self.db).get_list(search={"id": ("in", ids)})
        obj_map = {o.id: o for o in objs}
        for id_ in ids:
            if id_ not in obj_map:
                raise CustomException(msg="删除失败，该数据不存在")
        await ProduceComponentCRUD(self.auth, self.db).delete(ids=ids)

    async def set_available(self, data: BatchSetAvailable) -> None:
        await ProduceComponentCRUD(self.auth, self.db).set(ids=data.ids, status=data.status)

    @staticmethod
    def batch_export(obj_list: list[dict[str, Any]]) -> bytes:
        mapping_dict = {
            'project_id': '所属项目id',
            'name': '部件名称',
            'code': '部件编码',
            'count': '数量',
            'tmass': '总重',
            'id': '主键ID',
            'status': '是否启用(0:启用 1:禁用)',
            'description': '备注/描述',
            'created_time': '创建时间',
            'updated_time': '更新时间',
            'created_id': '创建人ID',
        }

        data = obj_list.copy()
        for item in data:
            item["status"] = "启用" if item.get("status") == 0 else "停用"
            creator_info = item.get("created_id")
            if isinstance(creator_info, dict):
                item["created_id"] = creator_info.get("name", "未知")
            else:
                item["created_id"] = "未知"

        return ExcelUtil.export_list2excel(list_data=data, mapping_dict=mapping_dict)

    async def batch_import(self, file: UploadFile, update_support: bool = False) -> str:
        header_dict = {
            '所属项目id': 'project_id',
            '部件名称': 'name',
            '部件编码': 'code',
            '数量': 'count',
            '总重': 'tmass',
            '是否启用(0:启用 1:禁用)': 'status',
            '备注/描述': 'description',
        }

        try:
            contents = await file.read()
            rows = ExcelUtil.read_excel_to_dicts(contents)
            await file.close()

            if not rows:
                raise CustomException(msg="导入文件为空")

            missing_headers = [h for h in header_dict if h not in rows[0]]
            if missing_headers:
                raise CustomException(msg=f"导入文件缺少必要的列: {', '.join(missing_headers)}")

            # 将中文字段名映射为英文字段
            mapped_rows = []
            for row in rows:
                mapped_rows.append({en: row.get(ch) for ch, en in header_dict.items()})

            required_fields = [
                "project_id",
                "name",
                "status",
            ]
            errors = []
            for field in required_fields:
                missing_indices = [i + 1 for i, r in enumerate(mapped_rows) if r.get(field) is None]
                if missing_indices:
                    field_name = next((k for k, v in header_dict.items() if v == field), field)
                    rows_str = "、".join(str(i) for i in missing_indices)
                    errors.append(f"{field_name}不能为空，第{rows_str}行")
            if errors:
                raise CustomException(msg=f"导入失败，以下行缺少必要字段：\n{'; '.join(errors)}")

            error_msgs = []
            success_count = 0

            for i, row in enumerate(mapped_rows, start=1):
                try:
                    create_schema = ProduceComponentCreateSchema.model_validate(row)

                    exists_obj = await ProduceComponentCRUD(self.auth, self.db).get(project_id=create_schema.project_id)
                    if exists_obj:
                        if update_support:
                            await ProduceComponentCRUD(self.auth, self.db).update(id=getattr(exists_obj, 'id'), data=create_schema)
                            success_count += 1
                        else:
                            error_msgs.append(f"第{i}行: 所属项目id {create_schema.project_id} 已存在")
                        continue
                    exists_obj = await ProduceComponentCRUD(self.auth, self.db).get(name=create_schema.name)
                    if exists_obj:
                        if update_support:
                            await ProduceComponentCRUD(self.auth, self.db).update(id=getattr(exists_obj, 'id'), data=create_schema)
                            success_count += 1
                        else:
                            error_msgs.append(f"第{i}行: 部件名称 {create_schema.name} 已存在")
                        continue

                    await ProduceComponentCRUD(self.auth, self.db).create(data=create_schema)
                    success_count += 1
                except Exception as e:
                    error_msgs.append(f"第{i}行: {e!s}")
                    continue

            result = f"成功导入 {success_count} 条数据"
            if error_msgs:
                result += "\n错误信息:\n" + "\n".join(error_msgs)
            return result

        except Exception as e:
            logger.error(f"批量导入失败: {e!s}")
            raise CustomException(msg=f"导入失败: {e!s}")

    @staticmethod
    def import_template_download() -> bytes:
        header_list = [
            '所属项目id',
            '部件名称',
            '部件编码',
            '数量',
            '总重',
            '是否启用(0:启用 1:禁用)',
            '备注/描述',
        ]
        selector_header_list = []
        option_list = []


        return ExcelUtil.get_excel_template(
            header_list=header_list,
            selector_header_list=selector_header_list,
            option_list=option_list,
        )
