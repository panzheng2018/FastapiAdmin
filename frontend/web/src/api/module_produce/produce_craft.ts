import { request } from "@utils";

// API 前缀来自分系统包 module_xxx → /xxx
// 对齐 module_example/demo：业务接口固定为 /{prefix}/{module_name}
const API_PATH = "/produce/produce_craft";

const ProduceCraftAPI = {
  getProduceCraftList(query: ProduceCraftPageQuery) {
    return request<ApiResponse<PageResult<ProduceCraftTable>>>({
      url: `${API_PATH}/list`,
      method: "get",
      params: query,
    });
  },

  getProduceCraftDetail(query: number) {
    return request<ApiResponse<ProduceCraftTable>>({
      url: `${API_PATH}/detail/${query}`,
      method: "get",
    });
  },

  createProduceCraft(body: ProduceCraftForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/create`,
      method: "post",
      data: body,
    });
  },

  updateProduceCraft(id: number, body: ProduceCraftForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/update/${id}`,
      method: "put",
      data: body,
    });
  },

  deleteProduceCraft(body: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}/delete`,
      method: "delete",
      data: body,
    });
  },

  batchProduceCraft(body: BatchType) {
    return request<ApiResponse>({
      url: `${API_PATH}/status/batch`,
      method: "patch",
      data: body,
    });
  },

  exportProduceCraft(body: ProduceCraftPageQuery) {
    return request<Blob>({
      url: `${API_PATH}/export`,
      method: "post",
      data: body,
      responseType: "blob",
    });
  },

  downloadTemplateProduceCraft() {
    return request<Blob>({
      url: `${API_PATH}/download/template`,
      method: "post",
      responseType: "blob",
    });
  },

  importProduceCraft(body: FormData) {
    return request<ApiResponse>({
      url: `${API_PATH}/import`,
      method: "post",
      data: body,
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
  },
};

export default ProduceCraftAPI;

// ------------------------------
// TS 类型声明
// ------------------------------

/** 列表查询参数 */
export interface ProduceCraftPageQuery extends PageQuery, UserByQueryParams {
  parent_id?: number;
  name?: string;
  position_id?: number;
  status?: string;
}

/** 列表展示项 */
export interface ProduceCraftTable extends BaseType {
  parent_id?: number;
  parent_name?: string;
  name?: string;
  position_id?: number;
  position_name?: string;
  status?: string;
  description?: string;
}

/** 新增/修改表单参数 */
export interface ProduceCraftForm extends BaseFormType {
  parent_id?: number;
  name?: string;
  position_id?: number;
  status?: string;
  description?: string;
}
