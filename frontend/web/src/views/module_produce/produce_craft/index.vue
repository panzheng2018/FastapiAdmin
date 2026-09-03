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
            :perm-create="['module_produce:produce_craft:create']"
            :perm-import="['module_produce:produce_craft:import']"
            :perm-export="['module_produce:produce_craft:export']"
            :perm-delete="['module_produce:produce_craft:delete']"
            :perm-patch="['module_produce:produce_craft:patch']"
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
          :label-width="96"
          label-position="left"
          :span="24"
          :gutter="0"
          :show-reset="false"
          :show-submit="false"
          class="crud-dialog-art-form"
        >
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
      default-template-file-name="produce_craft_import_template.xlsx"
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
import FaTableHeader from "@/components/tables/fa-table-header/index.vue";
import ProduceCraftAPI, {
  type ProduceCraftForm,
  type ProduceCraftPageQuery,
  type ProduceCraftTable,
} from "@/api/module_produce/produce_craft";

defineOptions({
  name: "ProduceCraft",
  inheritAttrs: false,
});


// 常量定义
const STATUS_OPTIONS = [
  { label: "启用", value: "0" },
  { label: "停用", value: "1" },
] as const;

const createInitialFormData = (): ProduceCraftForm => ({
  parent_id: undefined,
  name: undefined,
  status: "0",
  description: undefined,
});

type ProduceCraftSearchFormParams = {
  parent_id?: string;
  name?: string;
  status?: string;
} & AuditSearchFormParams;

const searchForm = ref<ProduceCraftSearchFormParams>({
  parent_id: undefined,
  name: undefined,
  status: undefined,
  created_id: undefined,
  updated_id: undefined,
  created_time: [],
  updated_time: [],
});

/** 搜索区域默认展开展示 */
const showSearchBar = ref(true);

const searchBarRef = ref<{ validate: () => Promise<boolean> } | null>(null);
const searchBarRules: Record<string, unknown> = {};

/** 业务搜索项（审计四字段由 FaSearchBar 的 includeAudit 属性追加） */
const businessSearchItems = computed(() => [
  {
    label: "父工艺ID",
    key: "parent_id",
    type: "input",
    placeholder: "请输入父工艺ID",
    clearable: true,
    span: 6,
  },
  {
    label: "工艺名称",
    key: "name",
    type: "input",
    placeholder: "请输入工艺名称",
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
  useTableSelection<ProduceCraftTable>();

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
    apiFn: ProduceCraftAPI.getProduceCraftList,
    apiParams: {
      page_no: 1,
      page_size: 10,
    },
    columnsFactory: (): ColumnOption<ProduceCraftTable>[] => [
      { type: "globalIndex", width: 56, label: "序号", align: "center", headerAlign: "center" },
      { type: "selection", width: 48, fixed: "left", align: "center", headerAlign: "center" },
      { prop: "parent_id", label: "父工艺ID", minWidth: 80, showOverflowTooltip: true, align: "center" },
      { prop: "name", label: "工艺名称", minWidth: 120, showOverflowTooltip: true, align: "center" },
      {
        prop: "status",
        label: "状态",
        width: 70,
        align: "center",
        headerAlign: "center",
        formatter: (row: ProduceCraftTable) => {
          const isEnabled = String(row.status) === "0";
          return h(
            ElTag,
            { type: isEnabled ? "success" : "danger" },
            () => (isEnabled ? "启用" : "禁用")
          );
        },
      },
      { prop: "description", label: "备注/描述", minWidth: 80, showOverflowTooltip: true, headerAlign: "center" },
      { prop: "created_time", label: "创建时间", width: 168, sortable: true, showOverflowTooltip: true, headerAlign: "center", visible: false },
      { prop: "updated_time", label: "更新时间", width: 168, sortable: true, showOverflowTooltip: true, headerAlign: "center", visible: false },
      {
        prop: "created_by",
        label: "创建人",
        minWidth: 100,
        headerAlign: "center",
        formatter: (row: ProduceCraftTable) => row.created_by?.name ?? "—",
        visible: false,
      },
      {
        prop: "updated_by",
        label: "更新人",
        minWidth: 100,
        headerAlign: "center",
        formatter: (row: ProduceCraftTable) => row.updated_by?.name ?? "—",
        visible: false,
      },
      {
        prop: "operation",
        label: "操作",
        width: 140,
        fixed: "right",
        align: "center",
        headerAlign: "center",
        formatter: (row: ProduceCraftTable) => formatOperationCell(row),
      },
    ],
  },
});

const crudCols = toCrudCols(columns);

const exportQueryParams = computed(() => {
  return stripPaginationParams(searchParams as Record<string, unknown>);
});

const importContentConfig = computed<IContentConfig>(() => ({
  permPrefix: "module_produce:produce_craft",
  cols: crudCols.value,
  indexAction: async () => ({}),
  importTemplate: () => ProduceCraftAPI.downloadTemplateProduceCraft(),
}));

const exportContentConfig = computed(() => ({
  permPrefix: "module_produce:produce_craft",
  cols: crudCols.value,
  exportsBlobAction: async (params: IObject) => {
    const merged = {
      ...(exportQueryParams.value as unknown as Record<string, unknown>),
      ...params,
    } as unknown as ProduceCraftPageQuery;
    const res = await ProduceCraftAPI.exportProduceCraft(merged);
    return res.data as Blob;
  },
}));

const { dialogVisible } = useCrudDialog();

const detailFormData = ref<ProduceCraftTable>({});

const detailItems: import("@/components/display/fa-descriptions/index.vue").DescriptionsItem[] = [
  { label: "父工艺ID", prop: "parent_id" },
  { label: "工艺名称", prop: "name" },
  { label: "状态", prop: "status", tag: { map: { "0": { type: "success", text: "启用" }, "1": { type: "danger", text: "禁用" } } } },
  { label: "备注/描述", prop: "description" },
  { label: "创建时间", prop: "created_time" },
  { label: "更新时间", prop: "updated_time" },
  { label: "创建人", prop: "created_by.name" },
  { label: "更新人", prop: "updated_by.name" },
];

const formData = ref<ProduceCraftForm>(createInitialFormData());

const rules = reactive({
  parent_id: [{ required: false, message: "请填写父工艺ID", trigger: "blur" }],
  name: [{ required: true, message: "请填写工艺名称", trigger: "blur" }],
  status: [{ required: true, message: "请填写是否启用(0:启用 1:禁用)", trigger: "blur" }],
  description: [{ required: false, message: "请填写备注/描述", trigger: "blur" }],
});

const dialogFormItems: FormItem[] = [
  {
    key: "parent_id",
    label: "父工艺ID",
    type: "number",
    props: {
      placeholder: "请输入父工艺ID",
      class: "w-full",
      style: { width: "100%" },
    },
  },
  { key: "name", label: "工艺名称", type: "input", props: { placeholder: "请输入工艺名称" } },
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

const crud = useCrudForm<ProduceCraftForm>({
  formData,
  initialFormData: createInitialFormData(),
  dialogVisible,
  dataFormRef,
  formRenderKey,
  detailApi: (id: number) => ProduceCraftAPI.getProduceCraftDetail(id),
  createApi: (data: ProduceCraftForm) => ProduceCraftAPI.createProduceCraft(data),
  updateApi: (id: number, data: ProduceCraftForm) => ProduceCraftAPI.updateProduceCraft(id, data),
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

const handleSearch = async (params: ProduceCraftSearchFormParams) => {
  await searchBarRef.value?.validate();
  replaceSearchParams({
    parent_id: params.parent_id,
    name: params.name,
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
    parent_id: undefined,
    name: undefined,
    status: undefined,
    created_id: undefined,
    updated_id: undefined,
    created_time: [],
    updated_time: [],
  };
  await resetSearchParams();
};

function buildRowActions(row: ProduceCraftTable): TableOperationAction[] {
  const all: TableOperationAction[] = [
    {
      key: "detail",
      label: "详情",
      artType: "view",
      perm: "module_produce:produce_craft:detail",
      run: () => void crud.handleOpenDialog("detail", row[PK] as number),
    },
    {
      key: "edit",
      label: "编辑",
      artType: "edit",
      icon: "ri:edit-2-line",
      perm: "module_produce:produce_craft:update",
      run: () => void crud.handleOpenDialog("update", row[PK] as number),
    },
    {
      key: "delete",
      label: "删除",
      artType: "delete",
      icon: "ri:delete-bin-4-line",
      perm: "module_produce:produce_craft:delete",
      run: () => deleteRow(row),
    },
  ];
  return all;
}

function formatOperationCell(row: ProduceCraftTable) {
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

const deleteRow = async (row: ProduceCraftTable) => {
  if (!row[PK]) return;
  try {
    await confirmDelete(`确定删除该工艺管理吗？此操作不可恢复！`);
    await ProduceCraftAPI.deleteProduceCraft([row[PK] as number]);
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
    await ProduceCraftAPI.deleteProduceCraft(ids);
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
    await ProduceCraftAPI.batchProduceCraft({ ids, status });
    // 成功 / 失败提示由 axios 拦截器统一处理
    faTableRef.value?.elTableRef?.clearSelection();
    await refreshData();
  } catch {
    // 用户取消
  }
}

async function handleCrudImportUpload(formData: FormData) {
  try {
    const res = await ProduceCraftAPI.importProduceCraft(formData);
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
  // 红色星号单独对齐，未设星号的行预留星号位置；标签文本恢复自然间距（无假空格）
  .el-form-item__label {
    position: relative;
    display: inline-flex;
    align-items: center;
    justify-content: flex-start;
    padding-left: 14px !important; // 预留红色星号的固定槽位
    box-sizing: border-box;
    white-space: pre; // 保持标签中的空格宽度不被浏览器折叠

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
  }
}
</style>
