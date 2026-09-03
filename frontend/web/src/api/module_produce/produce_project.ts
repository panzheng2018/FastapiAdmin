import { request } from "@utils";

// API 前缀来自分系统包 module_xxx → /xxx
// 对齐 module_example/demo：业务接口固定为 /{prefix}/{module_name}
const API_PATH = "/produce/produce_project";

const ProduceProjectAPI = {
  getProduceProjectList(query: ProduceProjectPageQuery) {
    return request<ApiResponse<PageResult<ProduceProjectTable>>>({
      url: `${API_PATH}/list`,
      method: "get",
      params: query,
    });
  },

  getProduceProjectDetail(query: number) {
    return request<ApiResponse<ProduceProjectTable>>({
      url: `${API_PATH}/detail/${query}`,
      method: "get",
    });
  },

  createProduceProject(body: ProduceProjectForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/create`,
      method: "post",
      data: body,
    });
  },

  updateProduceProject(id: number, body: ProduceProjectForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/update/${id}`,
      method: "put",
      data: body,
    });
  },

  deleteProduceProject(body: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}/delete`,
      method: "delete",
      data: body,
    });
  },

  batchProduceProject(body: BatchType) {
    return request<ApiResponse>({
      url: `${API_PATH}/status/batch`,
      method: "patch",
      data: body,
    });
  },

  exportProduceProject(body: ProduceProjectPageQuery) {
    return request<Blob>({
      url: `${API_PATH}/export`,
      method: "post",
      data: body,
      responseType: "blob",
    });
  },

  downloadTemplateProduceProject() {
    return request<Blob>({
      url: `${API_PATH}/download/template`,
      method: "post",
      responseType: "blob",
    });
  },

  importProduceProject(body: FormData) {
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

export default ProduceProjectAPI;

// ------------------------------
// TS 类型声明
// ------------------------------

/** 列表查询参数 */
export interface ProduceProjectPageQuery extends PageQuery, UserByQueryParams {
  name?: string;
  code?: string;
  no?: string;
  status?: string;
}

/** 列表展示项 */
export interface ProduceProjectTable extends BaseType {
  name?: string;
  code?: string;
  no?: string;
  status?: string;
  description?: string;
}

/** 新增/修改表单参数 */
export interface ProduceProjectForm extends BaseFormType {
  name?: string;
  code?: string;
  no?: string;
  status?: string;
  description?: string;
}
