import { request } from "@utils";

// API 前缀来自分系统包 module_xxx → /xxx
// 工时管理 API 路径: /produce/produce_workhour
const API_PATH = "/produce/produce_workhour";

const ProduceWorkhourAPI = {
  getProduceWorkhourList(query: ProduceWorkhourPageQuery) {
    return request<ApiResponse<PageResult<ProduceWorkhourTable>>>({
      url: `${API_PATH}/list`,
      method: "get",
      params: query,
    });
  },

  getProduceWorkhourDetail(query: number) {
    return request<ApiResponse<ProduceWorkhourTable>>({
      url: `${API_PATH}/detail/${query}`,
      method: "get",
    });
  },

  createProduceWorkhour(body: ProduceWorkhourForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/create`,
      method: "post",
      data: body,
    });
  },

  updateProduceWorkhour(id: number, body: ProduceWorkhourForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/update/${id}`,
      method: "put",
      data: body,
    });
  },

  deleteProduceWorkhour(body: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}/delete`,
      method: "delete",
      data: body,
    });
  },

  batchProduceWorkhour(body: BatchType) {
    return request<ApiResponse>({
      url: `${API_PATH}/status/batch`,
      method: "patch",
      data: body,
    });
  },

  exportProduceWorkhour(body: ProduceWorkhourPageQuery) {
    return request<Blob>({
      url: `${API_PATH}/export`,
      method: "post",
      data: body,
      responseType: "blob",
    });
  },

  downloadTemplateProduceWorkhour() {
    return request<Blob>({
      url: `${API_PATH}/download/template`,
      method: "post",
      responseType: "blob",
    });
  },

  importProduceWorkhour(body: FormData) {
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

export default ProduceWorkhourAPI;

// ------------------------------
// TS 类型声明
// ------------------------------

/** 列表查询参数 */
export interface ProduceWorkhourPageQuery extends PageQuery, UserByQueryParams {
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
export interface ProduceWorkhourTable extends BaseType {
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
export interface ProduceWorkhourForm extends BaseFormType {
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
