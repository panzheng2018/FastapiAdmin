<template>
  <div class="fa-full-height">
    <FaSearchBar
      v-show="showSearchBar"
      ref="searchBarRef"
      v-model="searchForm"
      :items="businessSearchItems"
      :rules="searchBarRules"
      :is-expand="false"
      :show-expand="true"
      :show-reset="true"
      :show-search="true"
      :disabled-search="false"
      :default-expanded="false"
      include-audit
      @search="handleSearch"
      @reset="onResetSearch"
    />

    <ElCard class="fa-table-card" :style="{ 'margin-top': showSearchBar ? '12px' : '0' }">
      <FaTableHeader
        v-model:columns="columnChecks"
        v-model:showSearchBar="showSearchBar"
        :loading="loading"
        @refresh="refreshData"
      >
        <template #left>
          <FaTableHeaderLeft
            :remove-ids="selectedIds"
            :perm-create="['module_produce:produce_component:create']"
            :perm-import="['module_produce:produce_component:import']"
            :perm-export="['module_produce:produce_component:export']"
            :perm-delete="['module_produce:produce_component:delete']"
            :perm-patch="['module_produce:produce_component:patch']"
            :delete-loading="batchDeleting"
            :create-loading="createLoading"
            @add="handleAdd"
            @import="openImport"
            @export="openExport"
            @delete="handleBatchDelete"
            @more="runBatchStatus"
          />
        </template>
      </FaTableHeader>

      <FaTable
        ref="faTableRef"
        :loading="loading"
        :data="data"
        :columns="columns"
        :pagination="pagination"
        @selection-change="onTableSelectionChange"
        @pagination:size-change="handleSizeChange"
        @pagination:current-change="handleCurrentChange"
      />
    </ElCard>

    <FaDialog
      v-model="dialogVisible.visible"
      :title="dialogVisible.title"
      width="500px"
      dialog-class="crud-embed-dialog"
      modal-class="crud-embed-dialog"
      :form-mode="dialogVisible.type"
      :confirm-loading="submitLoading"
      @cancel="handleCloseDialog"
      @close="handleCloseDialog"
      @confirm="handleSubmit()"
    >
      <template v-if="dialogVisible.type === 'detail'">
        <FaDescriptions
          :column="1"
          :data="detailFormData"
          :items="detailItems"
          max-height="70vh"
        />
      </template>
      <template v-else>
        <FaForm
          :key="formRenderKey"
          scrollbar
          max-height="70vh"
          ref="dataFormRef"
          v-model="formData"
          :items="dialogFormItems"
          :rules="rules"
          label-suffix=":"
          :label-width="100"
          label-position="left"
          :span="24"
          :gutter="0"
          :show-reset="false"
          :show-submit="false"
          class="crud-dialog-art-form"
        >
          <template #project_id>
            <ElSelect
              v-model="formData.project_id"
              placeholder="请选择所属项目"
              filterable
              clearable
              :loading="projectLoading"
              class="w-full"
              @visible-change="handleProjectDropdownVisible"
            >
              <ElOption
                v-for="item in projectList"
                :key="item.id"
                :label="item.name"
                :value="item.id!"
              >
                <div class="flex justify-between items-center w-full">
                  <span>{{ item.name }}</span>
                  <span class="text-xs text-[var(--el-text-color-secondary)] ml-2">
                    {{ item.code ? `(${item.code})` : '' }}
                  </span>
                </div>
              </ElOption>
              <template #footer>
                <div class="flex items-center justify-between px-3 py-1.5 border-t border-[var(--el-border-color-lighter)] bg-[var(--el-fill-color-light)] select-none">
                  <span class="text-xs text-[var(--el-text-color-secondary)]">
                    共 {{ projectTotal }} 条 (第 {{ projectPage }}/{{ totalProjectPages }} 页)
                  </span>
                  <div class="flex items-center gap-1">
                    <ElButton
                      size="small"
                      text
                      :disabled="projectPage <= 1"
                      @click.stop="fetchProjectOptions(projectPage - 1)"
                    >
                      上一页
                    </ElButton>
                    <ElButton
                      size="small"
                      text
                      :disabled="projectPage >= totalProjectPages"
                      @click.stop="fetchProjectOptions(projectPage + 1)"
                    >
                      下一页
                    </ElButton>
                  </div>
                </div>
              </template>
            </ElSelect>
          </template>
          <template #status>
            <div class="inline-flex items-center gap-2">
              <ElSwitch
                v-model="formData.status"
                active-value="0"
                inactive-value="1"
              />
              <span
                class="cursor-pointer select-none text-sm"
                :class="formData.status === '0' ? 'text-[var(--el-color-primary)]' : 'text-[var(--el-text-color-secondary)]'"
                @click="formData.status = formData.status === '0' ? '1' : '0'"
              >
                {{ formData.status === '0' ? '启用' : '停用' }}
              </span>
            </div>
          </template>
        </FaForm>
      </template>
    </FaDialog>

    <FaImportDialog
      v-model="importVisible"
      :content-config="importContentConfig"
      default-template-file-name="produce_component_import_template.xlsx"
      @upload="handleCrudImportUpload"
    />

    <FaExportDialog
      v-model="exportVisible"
      :content-config="exportContentConfig"
      :query-params="exportQueryParams"
      :page-data="data"
      :selection-data="selectedRows"
    />
  </div>
</template>

<script setup lang="ts">
import type { TableOperationAction } from "@/utils/table";
import { renderTableOperationCell, stripPaginationParams, toCrudCols } from "@utils";
import { useCrudForm } from "@/hooks/core/useCrudForm";
import { confirmDelete, confirmBatchDelete, confirmAction } from "@/hooks/core/useConfirm";
import { ResultEnum } from "@/enums/api/result.enum";
import type { IContentConfig, IObject } from "@/components/modal/types";
import type { AuditSearchFormParams } from "@/components/forms/fa-search-bar/auditSearchFormItems";
import type { FormItem } from "@/components/forms/fa-form/index.vue";
import type { ColumnOption } from "@/types/component";
import FaDescriptions from "@/components/display/fa-descriptions/index.vue";
import FaForm from "@/components/forms/fa-form/index.vue";
import { h } from "vue";
import { ElTag } from "element-plus";
import ProduceComponentAPI, {
  type ProduceComponentForm,
  type ProduceComponentPageQuery,
  type ProduceComponentTable,
} from "@/api/module_produce/produce_component";
import ProduceProjectAPI, {
  type ProduceProjectTable,
} from "@/api/module_produce/produce_project";

defineOptions({
  name: "ProduceComponent",
  inheritAttrs: false,
});


// 常量定义
const STATUS_OPTIONS = [
  { label: "启用", value: 0 },
  { label: "停用", value: 1 },
] as const;

const createInitialFormData = (): ProduceComponentForm => ({
  project_id: undefined,
  name: undefined,
  code: undefined,
  count: undefined,
  tmass: undefined,
  status: "0",
  description: undefined,
});

type ProduceComponentSearchFormParams = {
  project_id?: string;
  project_name?: string;
  name?: string;
  code?: string;
  count?: string;
  tmass?: string;
  status?: string;
} & AuditSearchFormParams;

const searchForm = ref<ProduceComponentSearchFormParams>({
  project_id: undefined,
  project_name: undefined,
  name: undefined,
  code: undefined,
  count: undefined,
  tmass: undefined,
  status: undefined,
  created_id: undefined,
  updated_id: undefined,
  created_time: [],
  updated_time: [],
});

/** 搜索区域默认展开展示（默认隐藏） */
const showSearchBar = ref(false);

const searchBarRef = ref<{ validate: () => Promise<boolean> } | null>(null);
const searchBarRules: Record<string, unknown> = {};

/** 业务搜索项（审计四字段由 FaSearchBar 的 includeAudit 属性追加） */
const businessSearchItems = computed(() => [
  {
    label: "所属项目",
    key: "project_name",
    type: "input",
    placeholder: "请输入所属项目",
    clearable: true,
    span: 6,
  },
  {
    label: "部件名称",
    key: "name",
    type: "input",
    placeholder: "请输入部件名称",
    clearable: true,
    span: 6,
  },
  {
    label: "部件编码",
    key: "code",
    type: "input",
    placeholder: "请输入部件编码",
    clearable: true,
    span: 6,
  },
  {
    label: "数量",
    key: "count",
    type: "input",
    placeholder: "请输入数量",
    clearable: true,
    span: 6,
  },
  {
    label: "总重",
    key: "tmass",
    type: "input",
    placeholder: "请输入总重",
    clearable: true,
    span: 6,
  },
  {
    label: "状态",
    key: "status",
    type: "select",
    props: {
      placeholder: "请选择状态",
      options: STATUS_OPTIONS,
      clearable: true,
    },
    span: 6,
  },
]);


const faTableRef = ref<{ elTableRef?: { clearSelection: () => void } } | null>(null);
const { selectedRows, selectedIds, batchDeleting, onTableSelectionChange } =
  useTableSelection<ProduceComponentTable>();

const createLoading = ref(false);

const PK = "id" as const;

const {
  columns,
  columnChecks,
  data,
  loading,
  pagination,
  searchParams,
  getData,
  replaceSearchParams,
  resetSearchParams,
  handleSizeChange,
  handleCurrentChange,
  refreshData,
  refreshCreate,
  refreshUpdate,
  refreshRemove,
} = useTable({
  core: {
    apiFn: ProduceComponentAPI.getProduceComponentList,
    apiParams: {
      page_no: 1,
      page_size: 10,
      order_by: JSON.stringify([{ id: "desc" }]),
    },
    columnsFactory: (): ColumnOption<ProduceComponentTable>[] => [
      { type: "globalIndex", width: 56, label: "序号", align: "center", headerAlign: "center" },
      { type: "selection", width: 48, fixed: "left", align: "center", headerAlign: "center" },
      {
        prop: "project_name",
        label: "所属项目",
        minWidth: 120,
        showOverflowTooltip: true,
        headerAlign: "center",
        formatter: (row: ProduceComponentTable) => row.project_name ?? (row.project_id ? String(row.project_id) : "—"),
      },
      { prop: "name", label: "部件名称", minWidth: 120, showOverflowTooltip: true, headerAlign: "center" },
      { prop: "code", label: "部件编码", minWidth: 70, showOverflowTooltip: true, headerAlign: "center" },
      { prop: "count", label: "数量", minWidth: 50, showOverflowTooltip: true, headerAlign: "center" },
      { prop: "tmass", label: "总重", minWidth: 70, showOverflowTooltip: true, headerAlign: "center" },
      {
        prop: "status",
        label: "状态",
        width: 70,
        align: "center",
        headerAlign: "center",
        formatter: (row: ProduceComponentTable) => {
          const isEnabled = String(row.status) === "0";
          return h(
            ElTag,
            { type: isEnabled ? "success" : "danger" },
            () => (isEnabled ? "启用" : "禁用")
          );
        },
      },
      { prop: "description", label: "备注/描述", minWidth: 80, showOverflowTooltip: true, headerAlign: "center", visible: false },
      { prop: "created_time", label: "创建时间", width: 168, sortable: true, showOverflowTooltip: true, headerAlign: "center", visible: false },
      { prop: "updated_time", label: "更新时间", width: 168, sortable: true, showOverflowTooltip: true, headerAlign: "center", visible: false },
      {
        prop: "created_by",
        label: "创建人",
        minWidth: 100,
        headerAlign: "center",
        formatter: (row: ProduceComponentTable) => row.created_by?.name ?? "—",
        visible: false,
      },
      {
        prop: "updated_by",
        label: "更新人",
        minWidth: 100,
        headerAlign: "center",
        formatter: (row: ProduceComponentTable) => row.updated_by?.name ?? "—",
        visible: false,
      },
      {
        prop: "operation",
        label: "操作",
        width: 140,
        fixed: "right",
        align: "center",
        headerAlign: "center",
        formatter: (row: ProduceComponentTable) => formatOperationCell(row),
      },
    ],
  },
});

const crudCols = toCrudCols(columns);

const exportQueryParams = computed(() => {
  return stripPaginationParams(searchParams as Record<string, unknown>);
});

const importContentConfig = computed<IContentConfig>(() => ({
  permPrefix: "module_produce:produce_component",
  cols: crudCols.value,
  indexAction: async () => ({}),
  importTemplate: () => ProduceComponentAPI.downloadTemplateProduceComponent(),
}));

const exportContentConfig = computed(() => ({
  permPrefix: "module_produce:produce_component",
  cols: crudCols.value,
  exportsBlobAction: async (params: IObject) => {
    const merged = {
      ...(exportQueryParams.value as unknown as Record<string, unknown>),
      ...params,
    } as unknown as ProduceComponentPageQuery;
    const res = await ProduceComponentAPI.exportProduceComponent(merged);
    return res.data as Blob;
  },
}));

const { dialogVisible } = useCrudDialog();

const detailFormData = ref<ProduceComponentTable>({});

const detailItems: import("@/components/display/fa-descriptions/index.vue").DescriptionsItem[] = [
  { label: "所属项目", prop: "project_name" },
  { label: "部件名称", prop: "name" },
  { label: "部件编码", prop: "code" },
  { label: "数量", prop: "count" },
  { label: "总重", prop: "tmass" },
  { label: "状态", prop: "status", tag: { map: { "0": { type: "success", text: "启用" }, "1": { type: "danger", text: "禁用" } } } },
  { label: "备注/描述", prop: "description" },
  { label: "创建时间", prop: "created_time" },
  { label: "更新时间", prop: "updated_time" },
  { label: "创建人", prop: "created_by.name" },
  { label: "更新人", prop: "updated_by.name" },
];

const projectList = ref<ProduceProjectTable[]>([]);
const projectTotal = ref(0);
const projectPage = ref(1);
const projectPageSize = ref(10);
const projectLoading = ref(false);

const totalProjectPages = computed(() =>
  Math.max(1, Math.ceil(projectTotal.value / projectPageSize.value))
);

const formData = ref<ProduceComponentForm>(createInitialFormData());

async function fetchProjectOptions(page = 1) {
  projectLoading.value = true;
  try {
    const res = await ProduceProjectAPI.getProduceProjectList({
      page_no: page,
      page_size: projectPageSize.value,
    });
    projectList.value = res.data.data?.items ?? [];
    projectTotal.value = res.data.data?.total ?? 0;
    projectPage.value = page;

    if (formData.value.project_id && !projectList.value.some((p) => p.id === formData.value.project_id)) {
      try {
        const detailRes = await ProduceProjectAPI.getProduceProjectDetail(formData.value.project_id);
        if (detailRes.data.data) {
          projectList.value = [detailRes.data.data, ...projectList.value];
        }
      } catch {
        // 忽略
      }
    }
  } catch (err) {
    if (import.meta.env.DEV) console.error("加载项目列表失败:", err);
  } finally {
    projectLoading.value = false;
  }
}

function handleProjectDropdownVisible(visible: boolean) {
  if (visible && projectList.value.length === 0) {
    fetchProjectOptions(1);
  }
}

watch(
  () => formData.value.project_id,
  async (newId) => {
    if (newId && !projectList.value.some((p) => p.id === newId)) {
      try {
        const detailRes = await ProduceProjectAPI.getProduceProjectDetail(newId);
        if (detailRes.data.data) {
          projectList.value = [detailRes.data.data, ...projectList.value];
        }
      } catch {
        // 忽略
      }
    }
  }
);

onMounted(() => {
  fetchProjectOptions(1);
});

const rules = reactive({
  project_id: [{ required: true, message: "请选择所属项目", trigger: "change" }],
  name: [{ required: true, message: "请填写部件名称", trigger: "blur" }],
  code: [{ required: false, message: "请填写部件编码", trigger: "blur" }],
  count: [{ required: false, message: "请填写数量", trigger: "blur" }],
  tmass: [{ required: false, message: "请填写总重", trigger: "blur" }],
  status: [{ required: true, message: "请选择状态", trigger: "change" }],
  description: [{ required: false, message: "请填写备注/描述", trigger: "blur" }],
});

const dialogFormItems: FormItem[] = [
  { key: "project_id", label: "所属项目", type: "select" },
  { key: "name", label: "部件名称", type: "input", props: { placeholder: "请输入部件名称" } },
  { key: "code", label: "部件编码", type: "input", props: { placeholder: "请输入部件编码" } },
  { key: "count", label: "数　　量", type: "number", props: { placeholder: "请输入数量", class: "w-full", style: { width: "100%" } } },
  { key: "tmass", label: "总　　重", type: "number", props: { placeholder: "请输入总重", class: "w-full", style: { width: "100%" } } },
  {
    key: "status",
    label: "状　　态",
    type: "switch",
  },
  {
    key: "description",
    label: "描　　述",
    type: "input",
    props: {
      type: "textarea",
      rows: 4,
      maxlength: 100,
      showWordLimit: true,
      placeholder: "请输入描述",
    },
  },
];

const dataFormRef = ref<InstanceType<typeof FaForm> | null>(null);
const formRenderKey = ref(0);

const crud = useCrudForm<ProduceComponentForm>({
  formData,
  initialFormData: createInitialFormData(),
  dialogVisible,
  dataFormRef,
  formRenderKey,
  detailApi: (id: number) => ProduceComponentAPI.getProduceComponentDetail(id),
  createApi: (data: ProduceComponentForm) => ProduceComponentAPI.createProduceComponent(data),
  updateApi: (id: number, data: ProduceComponentForm) => ProduceComponentAPI.updateProduceComponent(id, data),
  titles: { create: "新增", update: "修改", detail: "详情" },
  detailFormData,
  onCreateSuccess: async () => {
    await refreshCreate();
  },
  onUpdateSuccess: async () => {
    await refreshUpdate();
  },
});

const { submitLoading } = crud;

const { importVisible, exportVisible, openImport, openExport } = useImportExport();

const handleSearch = async (params: ProduceComponentSearchFormParams) => {
  await searchBarRef.value?.validate();
  replaceSearchParams({
    order_by: JSON.stringify([{ id: "desc" }]),
    project_id: params.project_id,
    project_name: params.project_name,
    name: params.name,
    code: params.code,
    count: params.count,
    tmass: params.tmass,
    status: params.status,
    created_id: params.created_id ?? undefined,
    updated_id: params.updated_id ?? undefined,
    created_time:
      Array.isArray(params.created_time) && params.created_time.length === 2
        ? params.created_time
        : undefined,
    updated_time:
      Array.isArray(params.updated_time) && params.updated_time.length === 2
        ? params.updated_time
        : undefined,
  } as Record<string, unknown>);
  await getData();
};

const onResetSearch = async () => {
  searchForm.value = {
    project_id: undefined,
    project_name: undefined,
    name: undefined,
    code: undefined,
    count: undefined,
    tmass: undefined,
    status: undefined,
    created_id: undefined,
    updated_id: undefined,
    created_time: [],
    updated_time: [],
  };
  await resetSearchParams();
};

function buildRowActions(row: ProduceComponentTable): TableOperationAction[] {
  const all: TableOperationAction[] = [
    {
      key: "detail",
      label: "详情",
      artType: "view",
      perm: "module_produce:produce_component:detail",
      run: () => void crud.handleOpenDialog("detail", row[PK] as number),
    },
    {
      key: "edit",
      label: "编辑",
      artType: "edit",
      icon: "ri:edit-2-line",
      perm: "module_produce:produce_component:update",
      run: () => void crud.handleOpenDialog("update", row[PK] as number),
    },
    {
      key: "delete",
      label: "删除",
      artType: "delete",
      icon: "ri:delete-bin-4-line",
      perm: "module_produce:produce_component:delete",
      run: () => deleteRow(row),
    },
  ];
  return all;
}

function formatOperationCell(row: ProduceComponentTable) {
  return renderTableOperationCell(buildRowActions(row), {
    wrapperClass: "inline-flex flex-wrap items-center justify-center gap-1.5 action-btn-group",
  });
}

async function handleAdd() {
  createLoading.value = true;
  try {
    await crud.handleOpenDialog("create");
  } finally {
    createLoading.value = false;
  }
}

async function handleCloseDialog() {
  await crud.handleCloseDialog();
}

async function handleSubmit() {
  await crud.handleSubmit();
}

const deleteRow = async (row: ProduceComponentTable) => {
  if (!row[PK]) return;
  try {
    await confirmDelete(`确定删除该部件管理吗？此操作不可恢复！`);
    await ProduceComponentAPI.deleteProduceComponent([row[PK] as number]);
    faTableRef.value?.elTableRef?.clearSelection();
    await refreshRemove();
  } catch {
    // 用户取消
  }
};

async function handleBatchDelete() {
  const ids = selectedIds.value;
  if (ids.length === 0) return;
  try {
    await confirmBatchDelete(ids.length);
    batchDeleting.value = true;
    await ProduceComponentAPI.deleteProduceComponent(ids);
    faTableRef.value?.elTableRef?.clearSelection();
    await refreshRemove();
  } catch {
    // 用户取消
  } finally {
    batchDeleting.value = false;
  }
}

async function runBatchStatus(value: "enable" | "disable") {
  const ids = selectedIds.value;
  if (ids.length === 0) {
    ElMessage.warning("请先在列表中勾选数据");
    return;
  }
  try {
    await confirmAction(
      `确认对选中的 ${ids.length} 条数据${value === "enable" ? "启用" : "停用"}？`,
      "批量设置"
    );
    const status = value === "enable" ? 0 : 1;
    await ProduceComponentAPI.batchProduceComponent({ ids, status });
    // 成功 / 失败提示由 axios 拦截器统一处理
    faTableRef.value?.elTableRef?.clearSelection();
    await refreshData();
  } catch {
    // 用户取消
  }
}

async function handleCrudImportUpload(formData: FormData) {
  try {
    const res = await ProduceComponentAPI.importProduceComponent(formData);
    if (res.data.code === ResultEnum.SUCCESS) {
      ElMessage.success(res.data.msg || "导入成功");
      importVisible.value = false;
      await refreshData();
    }
    // 非 SUCCESS 分支提示由 axios 拦截器统一处理
  } catch (error: unknown) {
    if (import.meta.env.DEV) console.error("[Import]", error);
    /* 接口错误已由拦截器提示 */
  }
}

</script>

<style lang="scss" scoped>
:deep(.crud-dialog-art-form) {
  // 红色星号单独对齐，未设星号的行预留星号位置；保持中文等宽对齐
  .el-form-item__label {
    position: relative;
    display: inline-flex;
    align-items: center;
    justify-content: flex-start;
    padding-left: 14px !important; // 预留红色星号的固定槽位
    box-sizing: border-box;
    white-space: pre; // 保持全角空格不被折叠

    // 必填项的红色星号绝对定位在左侧预留槽位中
    &::before {
      position: absolute;
      left: 2px;
      top: 50%;
      transform: translateY(-50%);
      margin-right: 0 !important;
      line-height: 1;
      width: 10px;
      text-align: center;
    }
  }

  // 表单文本输入控件撑满
  .el-form-item__content {
    .el-input,
    .el-input-number,
    .el-textarea {
      width: 100%;
    }
  }
}

:deep(.action-btn-group) {
  gap: 6px !important;

  .hover-btn {
    margin-right: 0 !important;
    width: 32px !important;
    height: 32px !important;
    min-width: 32px !important;
    padding: 0 !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;

    // 第1个（详情）与第3个（删除）图标为 16px
    .fa-svg-icon {
      font-size: 16px !important;
      width: 16px !important;
      height: 16px !important;
    }
  }

  // 第2个（编辑）图标为 18px
  span:nth-child(2) .hover-btn .fa-svg-icon {
    font-size: 18px !important;
    width: 18px !important;
    height: 18px !important;
  }
}

:deep(.el-dialog__header) { padding-top: 0px !important; }

:deep(.el-dialog__footer) { padding-bottom: 0px !important; }

:deep(.crud-dialog-art-form) {
  // 移除组件自带的 pt-4 (16px)
  padding-top: 0 !important;
  // 隐藏按钮空槽
  .el-col:has(.mb-3) { display: none; }
  // 描述的输入框
  .el-form-item:has(.el-textarea) { margin-bottom: 0px !important; }
}

</style>
