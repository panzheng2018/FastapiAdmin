import { request } from "@utils";

// API 前缀来自分系统包 module_xxx → /xxx
// 对齐 module_example/demo：业务接口固定为 /{prefix}/{module_name}
const API_PATH = "/produce/produce_component";

const ProduceComponentAPI = {
  getProduceComponentList(query: ProduceComponentPageQuery) {
    return request<ApiResponse<PageResult<ProduceComponentTable>>>({
      url: `${API_PATH}/list`,
      method: "get",
      params: query,
    });
  },

  getProduceComponentDetail(query: number) {
    return request<ApiResponse<ProduceComponentTable>>({
      url: `${API_PATH}/detail/${query}`,
      method: "get",
    });
  },

  createProduceComponent(body: ProduceComponentForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/create`,
      method: "post",
      data: body,
    });
  },

  updateProduceComponent(id: number, body: ProduceComponentForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/update/${id}`,
      method: "put",
      data: body,
    });
  },

  deleteProduceComponent(body: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}/delete`,
      method: "delete",
      data: body,
    });
  },

  batchProduceComponent(body: BatchType) {
    return request<ApiResponse>({
      url: `${API_PATH}/status/batch`,
      method: "patch",
      data: body,
    });
  },

  exportProduceComponent(body: ProduceComponentPageQuery) {
    return request<Blob>({
      url: `${API_PATH}/export`,
      method: "post",
      data: body,
      responseType: "blob",
    });
  },

  downloadTemplateProduceComponent() {
    return request<Blob>({
      url: `${API_PATH}/download/template`,
      method: "post",
      responseType: "blob",
    });
  },

  importProduceComponent(body: FormData) {
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

export default ProduceComponentAPI;

// ------------------------------
// TS 类型声明
// ------------------------------

/** 列表查询参数 */
export interface ProduceComponentPageQuery extends PageQuery, UserByQueryParams {
  project_id?: number;
  project_name?: string;
  name?: string;
  code?: string;
  count?: number;
  tmass?: number;
  status?: string;
}

/** 列表展示项 */
export interface ProduceComponentTable extends BaseType {
  project_id?: number;
  project_name?: string;
  name?: string;
  code?: string;
  count?: number;
  tmass?: number;
  status?: string;
  description?: string;
}

/** 新增/修改表单参数 */
export interface ProduceComponentForm extends BaseFormType {
  project_id?: number;
  name?: string;
  code?: string;
  count?: number;
  tmass?: number;
  status?: string;
  description?: string;
}
