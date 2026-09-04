import { request } from "@utils";

// API 前缀来自分系统包 module_xxx → /xxx
// 对齐 module_example/demo：业务接口固定为 /{prefix}/{module_name}
const API_PATH = "/produce/produce_worder";

const ProduceWorderAPI = {
  getProduceWorderList(query: ProduceWorderPageQuery) {
    return request<ApiResponse<PageResult<ProduceWorderTable>>>({
      url: `${API_PATH}/list`,
      method: "get",
      params: query,
    });
  },

  getProduceWorderDetail(query: number) {
    return request<ApiResponse<ProduceWorderTable>>({
      url: `${API_PATH}/detail/${query}`,
      method: "get",
    });
  },

  createProduceWorder(body: ProduceWorderForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/create`,
      method: "post",
      data: body,
    });
  },

  updateProduceWorder(id: number, body: ProduceWorderForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/update/${id}`,
      method: "put",
      data: body,
    });
  },

  deleteProduceWorder(body: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}/delete`,
      method: "delete",
      data: body,
    });
  },

  batchProduceWorder(body: BatchType) {
    return request<ApiResponse>({
      url: `${API_PATH}/status/batch`,
      method: "patch",
      data: body,
    });
  },

  exportProduceWorder(body: ProduceWorderPageQuery) {
    return request<Blob>({
      url: `${API_PATH}/export`,
      method: "post",
      data: body,
      responseType: "blob",
    });
  },

  downloadTemplateProduceWorder() {
    return request<Blob>({
      url: `${API_PATH}/download/template`,
      method: "post",
      responseType: "blob",
    });
  },

  importProduceWorder(body: FormData) {
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

export default ProduceWorderAPI;

// ------------------------------
// TS 类型声明
// ------------------------------

/** 列表查询参数 */
export interface ProduceWorderPageQuery extends PageQuery, UserByQueryParams {
  order_by?: string;
  no?: string;
  component_id?: number;
  craft_id?: number;
  man_hour?: number;
  plan_count?: number;
  real_count?: number;
  plan_end_time?: string;
  real_end_time?: string;
  plan_user_id?: number;
  real_user_id?: number;
  status?: string;
}

/** 列表展示项 */
export interface ProduceWorderTable extends BaseType {
  no?: string;
  project_id?: number;
  project_name?: string;
  component_id?: number;
  component_name?: string;
  craft_id?: number;
  craft_name?: string;
  man_hour?: number;
  plan_count?: number;
  real_count?: number;
  plan_end_time?: string;
  real_end_time?: string;
  plan_user_id?: number;
  plan_user_name?: string;
  real_user_id?: number;
  real_user_name?: string;
  status?: string;
  description?: string;
}

/** 新增/修改表单参数 */
export interface ProduceWorderForm extends BaseFormType {
  no?: string;
  project_id?: number;
  component_id?: number;
  craft_id?: number;
  man_hour?: number;
  plan_count?: number;
  real_count?: number;
  plan_end_time?: string;
  real_end_time?: string;
  plan_user_id?: number;
  real_user_id?: number;
  status?: string;
  description?: string;
}
