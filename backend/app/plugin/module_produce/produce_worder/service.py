# -*- coding: utf-8 -*-

from datetime import datetime
from typing import Any

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.base_schema import AuthSchema, BatchSetAvailable, PageResultSchema
from app.core.exceptions import CustomException
from app.core.logger import logger
from app.utils.common_util import search_to_dict
from app.utils.excel_util import ExcelUtil

from .crud import ProduceWorderCRUD
from .schema import (
    ProduceWorderCreateSchema,
    ProduceWorderOutSchema,
    ProduceWorderQueryParam,
    ProduceWorderUpdateSchema,
)


class ProduceWorderService:
    """工单管理模块服务层"""

    def __init__(self, auth: AuthSchema, db: AsyncSession) -> None:
        self.auth = auth
        self.db = db

    @staticmethod
    def _populate_names(item: ProduceWorderOutSchema, obj: Any) -> ProduceWorderOutSchema:
        if getattr(obj, "craft", None):
            item.craft_name = obj.craft.name
        if getattr(obj, "plan_user", None):
            item.plan_user_name = obj.plan_user.name or obj.plan_user.username
        if getattr(obj, "real_user", None):
            item.real_user_name = obj.real_user.name or obj.real_user.username
        if getattr(obj, "component", None):
            item.component_name = obj.component.name
            if getattr(obj.component, "project", None):
                item.project_name = obj.component.project.name
                item.project_id = obj.component.project.id
        return item

    async def detail(self, id: int) -> ProduceWorderOutSchema:
        obj = await ProduceWorderCRUD(self.auth, self.db).get(
            id=id, preload=["craft", "plan_user", "real_user", "component", "component.project"]
        )
        if not obj:
            raise CustomException(msg="该数据不存在")
        item = ProduceWorderOutSchema.model_validate(obj)
        return self._populate_names(item, obj)

    async def get_list(
        self,
        search: ProduceWorderQueryParam | None = None,
        order_by: list[dict[str, str]] | None = None,
    ) -> list[ProduceWorderOutSchema]:
        obj_list = await ProduceWorderCRUD(self.auth, self.db).get_list(
            search=search_to_dict(search),
            order_by=order_by,
            preload=["craft", "plan_user", "real_user", "component", "component.project"],
        )
        result = []
        for obj in obj_list:
            item = ProduceWorderOutSchema.model_validate(obj)
            result.append(self._populate_names(item, obj))
        return result

    async def page(
        self,
        page_no: int,
        page_size: int,
        search: ProduceWorderQueryParam | None = None,
        order_by: list[dict[str, str]] | None = None,
    ) -> PageResultSchema[ProduceWorderOutSchema]:
        offset = (page_no - 1) * page_size
        page_result = await ProduceWorderCRUD(self.auth, self.db).page(
            offset=offset,
            limit=page_size,
            order_by=order_by or [{"id": "asc"}],
            search=search_to_dict(search, {}),
            preload=["craft", "plan_user", "real_user", "component", "component.project"],
        )
        items: list[ProduceWorderOutSchema] = []
        for obj in page_result.items:
            item = ProduceWorderOutSchema.model_validate(obj)
            items.append(self._populate_names(item, obj))
        page_result.items = items
        return page_result

    async def create(self, data: ProduceWorderCreateSchema) -> ProduceWorderOutSchema:
        obj = await ProduceWorderCRUD(self.auth, self.db).get(no=data.no)
        if obj:
            raise CustomException(msg="创建失败，单号已存在")
        if data.real_user_id is None:
            data.real_user_id = data.plan_user_id
        obj = await ProduceWorderCRUD(self.auth, self.db).create(data=data)
        return await self.detail(obj.id)

    async def update(self, id: int, data: ProduceWorderUpdateSchema) -> ProduceWorderOutSchema:
        obj = await ProduceWorderCRUD(self.auth, self.db).get(id=id)
        if not obj:
            raise CustomException(msg="更新失败，该数据不存在")

        if data.no:
            exist_obj = await ProduceWorderCRUD(self.auth, self.db).get(no=data.no)
            if exist_obj and exist_obj.id != id:
                raise CustomException(msg="更新失败，单号重复")

        # 状态修改为 "4"（已完成）时，同时将实际时间设置为后端服务器当前时间
        if str(data.status) == "4":
            data.real_end_time = datetime.now()

        obj = await ProduceWorderCRUD(self.auth, self.db).update(id=id, data=data)
        return await self.detail(id)

    async def delete(self, ids: list[int]) -> None:
        if not ids:
            raise CustomException(msg="删除失败，删除对象不能为空")
        objs = await ProduceWorderCRUD(self.auth, self.db).get_list(search={"id": ("in", ids)})
        obj_map = {o.id: o for o in objs}
        for id_ in ids:
            if id_ not in obj_map:
                raise CustomException(msg="删除失败，该数据不存在")
        await ProduceWorderCRUD(self.auth, self.db).delete(ids=ids)

    async def set_available(self, data: BatchSetAvailable) -> None:
        await ProduceWorderCRUD(self.auth, self.db).set(ids=data.ids, status=data.status)

    @staticmethod
    def batch_export(obj_list: list[dict[str, Any]]) -> bytes:
        mapping_dict = {
            'no': '单号',
            'component_id': '部件id',
            'craft_id': '工艺id',
            'man_hour': '工时',
            'plan_count': '计划数量',
            'real_count': '实际数量',
            'plan_end_time': '计划完工时间',
            'real_end_time': '实际时间',
            'plan_user_id': '计划执行用户',
            'real_user_id': '实际用户',
            'id': '工单ID',
            'status': '状态 0=启用 1=禁用 2=待生产 3=生产中 4=已完成 5=已取消 6=已暂停',
            'description': '备注/描述',
            'created_time': '创建时间',
            'updated_time': '更新时间',
            'created_id': '创建人ID',
        }

        data = obj_list.copy()
        status_map = {
            "0": "启用",
            "1": "禁用",
            "2": "待生产",
            "3": "生产中",
            "4": "已完成",
            "5": "已取消",
            "6": "已暂停",
        }
        for item in data:
            item["status"] = status_map.get(str(item.get("status")), str(item.get("status") or ""))
            creator_info = item.get("created_id")
            if isinstance(creator_info, dict):
                item["created_id"] = creator_info.get("name", "未知")
            else:
                item["created_id"] = "未知"

        return ExcelUtil.export_list2excel(list_data=data, mapping_dict=mapping_dict)

    async def batch_import(self, file: UploadFile, update_support: bool = False) -> str:
        header_dict = {
            '单号': 'no',
            '部件id': 'component_id',
            '工艺id': 'craft_id',
            '工时': 'man_hour',
            '计划数量': 'plan_count',
            '实际数量': 'real_count',
            '计划完工时间': 'plan_end_time',
            '实际时间': 'real_end_time',
            '计划执行用户': 'plan_user_id',
            '实际用户': 'real_user_id',
            '状态 0=启用 1=禁用 2=待生产 3=生产中 4=已完成 5=已取消 6=已暂停': 'status',
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
            status_reverse = {
                "启用": "0",
                "禁用": "1",
                "待生产": "2",
                "生产中": "3",
                "已完成": "4",
                "已取消": "5",
                "已暂停": "6",
            }
            for row in rows:
                item = {en: row.get(ch) for ch, en in header_dict.items()}
                if "status" in item and item["status"] is not None:
                    item["status"] = status_reverse.get(str(item["status"]).strip(), str(item["status"]).strip())
                mapped_rows.append(item)

            required_fields = [
                "no",
                "component_id",
                "craft_id",
                "man_hour",
                "plan_count",
                "plan_end_time",
                "plan_user_id",
                "real_user_id",
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
                    create_schema = ProduceWorderCreateSchema.model_validate(row)

                    exists_obj = await ProduceWorderCRUD(self.auth, self.db).get(no=create_schema.no)
                    if exists_obj:
                        if update_support:
                            await ProduceWorderCRUD(self.auth, self.db).update(id=getattr(exists_obj, 'id'), data=create_schema)
                            success_count += 1
                        else:
                            error_msgs.append(f"第{i}行: 单号 {create_schema.no} 已存在")
                        continue

                    await ProduceWorderCRUD(self.auth, self.db).create(data=create_schema)
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
            '单号',
            '部件id',
            '工艺id',
            '工时',
            '计划数量',
            '实际数量',
            '计划完工时间',
            '实际时间',
            '计划执行用户',
            '实际用户',
            '状态 0=启用 1=禁用 2=待生产 3=生产中 4=已完成 5=已取消 6=已暂停',
            '备注/描述',
        ]
        selector_header_list = []
        option_list = []


        return ExcelUtil.get_excel_template(
            header_list=header_list,
            selector_header_list=selector_header_list,
            option_list=option_list,
        )
