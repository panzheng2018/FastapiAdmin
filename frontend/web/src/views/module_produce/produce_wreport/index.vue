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
            :perm-create="['module_produce:produce_wreport:create']"
            :perm-import="['module_produce:produce_wreport:import']"
            :perm-export="['module_produce:produce_wreport:export']"
            :perm-delete="['module_produce:produce_wreport:delete']"
            :perm-patch="['module_produce:produce_wreport:patch']"
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
          <!-- 1. 单号：输入框 + 生成按钮 -->
          <template #no>
            <div class="flex items-center gap-2 w-full custom-input-container">
              <ElInput
                v-model="formData.no"
                placeholder="请输入单号"
                clearable
                class="flex-1"
              />
              <ElButton type="primary" plain @click="handleGenerateNo">生成</ElButton>
            </div>
          </template>

          <!-- 2. 所属项目：下拉菜单（对齐部件管理带分页底栏） -->
          <template #project_id>
            <ElSelect
              v-model="formData.project_id"
              placeholder="请选择所属项目"
              filterable
              clearable
              :loading="projectLoading"
              class="w-full custom-input-container"
              @change="handleProjectChange"
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

          <!-- 3. 所属部件：下拉菜单（对齐部件管理带分页底栏，按所属项目筛选） -->
          <template #component_id>
            <ElSelect
              v-model="formData.component_id"
              placeholder="请选择所属部件"
              filterable
              clearable
              :loading="componentLoading"
              class="w-full custom-input-container"
              :disabled="!formData.project_id"
              @visible-change="handleComponentDropdownVisible"
            >
              <ElOption
                v-for="item in componentList"
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
                    共 {{ componentTotal }} 条 (第 {{ componentPage }}/{{ totalComponentPages }} 页)
                  </span>
                  <div class="flex items-center gap-1">
                    <ElButton
                      size="small"
                      text
                      :disabled="componentPage <= 1"
                      @click.stop="fetchComponentOptions(componentPage - 1)"
                    >
                      上一页
                    </ElButton>
                    <ElButton
                      size="small"
                      text
                      :disabled="componentPage >= totalComponentPages"
                      @click.stop="fetchComponentOptions(componentPage + 1)"
                    >
                      下一页
                    </ElButton>
                  </div>
                </div>
              </template>
            </ElSelect>
          </template>

          <!-- 4. 工艺：下拉菜单（仅显示没有父工艺id的根工艺） -->
          <template #craft_id>
            <ElSelect
              v-model="formData.craft_id"
              placeholder="请选择工艺"
              filterable
              clearable
              :loading="craftLoading"
              class="w-full custom-input-container craft-select-center"
            >
              <ElOption
                v-for="item in rootCraftList"
                :key="item.id"
                :label="item.name"
                :value="item.id!"
                style="text-align: center;"
              />
            </ElSelect>
          </template>

          <!-- 5. 执行用户：下拉菜单（根据选中工艺的岗位ID动态过滤；普通用户固定为自己） -->
          <template #plan_user_id>
            <ElSelect
              v-model="formData.plan_user_id"
              :placeholder="!isSuperuser ? (userStore.info.name || userStore.info.username || '当前用户') : (!formData.craft_id ? '请先选择工艺' : (targetPositionName ? `请选择${targetPositionName}` : '请选择执行用户'))"
              :disabled="!isSuperuser || !formData.craft_id"
              filterable
              :clearable="isSuperuser"
              :loading="userLoading"
              class="w-full custom-input-container"
              :no-data-text="!formData.craft_id ? '请先选择工艺' : (targetPositionId ? '该岗位暂无配置人员' : '无可选用户')"
            >
              <ElOption
                v-for="u in filteredPlanUserList"
                :key="u.id"
                :label="u.name || u.username"
                :value="u.id!"
              >
                <div class="flex justify-between items-center w-full">
                  <span>{{ u.name || u.username }}</span>
                  <span class="text-xs text-[var(--el-text-color-secondary)] ml-2">
                    {{ u.username ? `(${u.username})` : '' }}
                  </span>
                </div>
              </ElOption>
            </ElSelect>
          </template>
        </FaForm>
      </template>
    </FaDialog>

    <FaImportDialog
      v-model="importVisible"
      :content-config="importContentConfig"
      default-template-file-name="produce_wreport_import_template.xlsx"
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
import FaTableHeader from "@/components/tables/fa-table-header/index.vue";
import ProduceWreportAPI, {
  type ProduceWreportForm,
  type ProduceWreportPageQuery,
  type ProduceWreportTable,
} from "@/api/module_produce/produce_wreport";
import ProduceProjectAPI, {
  type ProduceProjectTable,
} from "@/api/module_produce/produce_project";
import ProduceComponentAPI, {
  type ProduceComponentTable,
} from "@/api/module_produce/produce_component";
import ProduceCraftAPI, {
  type ProduceCraftTable,
} from "@/api/module_produce/produce_craft";
import { UserAPI, type UserInfo } from "@/api/module_system/user";
import { useUserStore } from "@stores";
import { computed, h, onMounted, reactive, ref, watch } from "vue";
import { ElTag, ElMessage } from "element-plus";

defineOptions({
  name: "ProduceWreport",
  inheritAttrs: false,
});

const userStore = useUserStore();
const isSuperuser = computed(() => !!userStore.info.is_superuser);
const currentUserId = computed(() => userStore.info.id);

// 常量定义
const STATUS_CONFIG: Record<string, { type: "info" | "primary" | "success" | "danger" | "warning"; text: string }> = {
  "0": { type: "success", text: "启用" },
  "1": { type: "danger", text: "禁用" },
  "2": { type: "info", text: "待生产" },
  "3": { type: "primary", text: "生产中" },
  "4": { type: "success", text: "已完成" },
  "5": { type: "danger", text: "已取消" },
  "6": { type: "warning", text: "已暂停" },
};

const STATUS_OPTIONS = [
  { label: "启用", value: "0" },
  { label: "禁用", value: "1" },
  { label: "待生产", value: "2" },
  { label: "生产中", value: "3" },
  { label: "已完成", value: "4" },
  { label: "已取消", value: "5" },
  { label: "已暂停", value: "6" },
] as const;

/** 格式化日期时间为两行（第1行日期，第2行时间，日期中的-与时间中的:严格垂直对齐） */
function formatDateTimeTwoLines(val?: string | null) {
  if (!val) return "—";
  const str = String(val).trim();
  const parts = str.includes(" ")
    ? str.split(" ")
    : str.includes("T")
    ? str.split("T")
    : [str];
  const dateStr = parts[0] || "";
  const timeStr = parts.slice(1).join(" ");

  if (!timeStr) {
    return h("span", { style: { fontSize: "13px", color: "var(--el-text-color-primary, #303133)" } }, dateStr);
  }

  const dateMatch = dateStr.match(/^(\d{4})-(\d{2})-(\d{2})$/);
  const timeMatch = timeStr.match(/^(\d{1,2}):(\d{2})(?::(\d{2}))?$/);

  if (!dateMatch || !timeMatch) {
    return h(
      "div",
      {
        class: "inline-flex flex-col items-end justify-center leading-none select-none text-right",
        style: { lineHeight: "1.15", fontSize: "13px" },
      },
      [
        h("span", { style: { color: "var(--el-text-color-primary, #303133)", whiteSpace: "nowrap" } }, dateStr),
        h("span", { style: { color: "var(--el-text-color-regular, #606266)", marginTop: "2px", whiteSpace: "nowrap" } }, timeStr),
      ]
    );
  }

  const [, y, m, d] = dateMatch;
  const [, hh, mm, ss] = timeMatch;

  const sepStyle = {
    justifySelf: "center",
    textAlign: "center" as const,
    width: "8px",
    color: "var(--el-text-color-secondary, #909399)",
  };

  return h(
    "div",
    {
      class: "inline-grid select-none",
      style: {
        gridTemplateColumns: "auto 8px auto 8px auto",
        rowGap: "2px",
        lineHeight: "1.15",
        fontSize: "13px",
        fontVariantNumeric: "tabular-nums",
        fontFeatureSettings: '"tnum"',
        fontFamily:
          '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
      },
    },
    [
      // 第 1 行：日期 (YYYY - MM - DD)
      h("span", { style: { justifySelf: "end", color: "var(--el-text-color-primary, #303133)" } }, y),
      h("span", { style: sepStyle }, "-"),
      h("span", { style: { justifySelf: "center", color: "var(--el-text-color-primary, #303133)" } }, m),
      h("span", { style: sepStyle }, "-"),
      h("span", { style: { justifySelf: "center", color: "var(--el-text-color-primary, #303133)" } }, d),

      // 第 2 行：时间 (  HH : mm : ss)
      h("span", { style: { justifySelf: "end", color: "var(--el-text-color-regular, #606266)" } }, hh),
      h("span", { style: sepStyle }, ":"),
      h("span", { style: { justifySelf: "center", color: "var(--el-text-color-regular, #606266)" } }, mm),
      h("span", { style: sepStyle }, ss ? ":" : ""),
      h("span", { style: { justifySelf: "center", color: "var(--el-text-color-regular, #606266)" } }, ss || ""),
    ]
  );
}

const createInitialFormData = (): ProduceWreportForm => ({
  no: undefined,
  project_id: undefined,
  component_id: undefined,
  craft_id: undefined,
  man_hour: 0,
  plan_count: 1,
  real_count: undefined,
  plan_end_time: undefined,
  real_end_time: undefined,
  plan_user_id: !isSuperuser.value ? currentUserId.value : undefined,
  real_user_id: !isSuperuser.value ? currentUserId.value : undefined,
  status: "2",
  description: undefined,
});

type ProduceWreportSearchFormParams = {
  no?: string;
  component_id?: string;
  craft_id?: string;
  plan_count?: string;
  real_count?: string;
  plan_end_time?: string;
  real_end_time?: string;
  plan_user_id?: string;
  real_user_id?: string;
  status?: string;
} & AuditSearchFormParams;

const searchForm = ref<ProduceWreportSearchFormParams>({
  no: undefined,
  component_id: undefined,
  craft_id: undefined,
  plan_count: undefined,
  real_count: undefined,
  plan_end_time: undefined,
  real_end_time: undefined,
  plan_user_id: undefined,
  real_user_id: undefined,
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

/** 业务搜索项（超级管理员可搜索任意执行用户，非管理员只能查看自己的工单故无需该搜索项） */
const businessSearchItems = computed(() => {
  const items: any[] = [
    {
      label: "单号",
      key: "no",
      type: "input",
      placeholder: "请输入单号",
      clearable: true,
      span: 6,
    },
    {
      label: "所属部件",
      key: "component_id",
      type: "input",
      placeholder: "请输入所属部件",
      clearable: true,
      span: 6,
    },
    {
      label: "数量",
      key: "plan_count",
      type: "input",
      placeholder: "请输入数量",
      clearable: true,
      span: 6,
    },
    {
      label: "工艺",
      key: "craft_id",
      type: "input",
      placeholder: "请输入工艺",
      clearable: true,
      span: 6,
    },
    {
      label: "完工时间",
      key: "plan_end_time",
      type: "date-picker",
      props: {
        type: "date",
        valueFormat: "YYYY-MM-DD",
        clearable: true,
        placeholder: "请选择完工时间",
      },
      span: 6,
    },
  ];

  if (isSuperuser.value) {
    items.push({
      label: "执行用户",
      key: "plan_user_id",
      type: "input",
      placeholder: "请输入执行用户",
      clearable: true,
      span: 6,
    });
  }

  items.push({
    label: "状态",
    key: "status",
    type: "select",
    props: {
      placeholder: "请选择状态",
      options: STATUS_OPTIONS,
      clearable: true,
    },
    span: 6,
  });

  return items;
});


const faTableRef = ref<{ elTableRef?: { clearSelection: () => void } } | null>(null);
const { selectedRows, selectedIds, batchDeleting, onTableSelectionChange } =
  useTableSelection<ProduceWreportTable>();

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
    apiFn: ProduceWreportAPI.getProduceWreportList,
    apiParams: {
      page_no: 1,
      page_size: 10,
      order_by: JSON.stringify([{ id: "desc" }]),
    },
    columnsFactory: (): ColumnOption<ProduceWreportTable>[] => [
      { type: "globalIndex", label: "序号", width: 50, fixed: "left", align: "center", headerAlign: "center", visible: false },
      { type: "selection", width: 45, fixed: "left", align: "center", headerAlign: "center" },
      { prop: "no", label: "单号", minWidth: 120, fixed: "left", showOverflowTooltip: true, headerAlign: "center" },
      {
        prop: "project_name",
        label: "所属项目",
        minWidth: 120,
        fixed: "left",
        showOverflowTooltip: true,
        headerAlign: "center",
        formatter: (row: ProduceWreportTable) => row.project_name || "—",
      },
      {
        prop: "component_id",
        label: "所属部件",
        minWidth: 120,
        fixed: "left",
        showOverflowTooltip: true,
        headerAlign: "center",
        formatter: (row: ProduceWreportTable) => row.component_name || row.component_id || "—",
      },
      { prop: "plan_count", label: "数量", minWidth: 55, showOverflowTooltip: true, align: "center" },
      {
        prop: "craft_id",
        label: "工艺",
        minWidth: 55,
        showOverflowTooltip: true,
        align: "center",
        formatter: (row: ProduceWreportTable) => {
          return (
            row.craft_name ||
            craftList.value.find((c) => c.id === row.craft_id)?.name ||
            "—"
          );
        },
      },
      { prop: "man_hour", label: "工时", minWidth: 80, showOverflowTooltip: true, headerAlign: "center" },
      { prop: "real_count", label: "实际数量", minWidth: 80, showOverflowTooltip: true, headerAlign: "center", visible: false },
      {
        prop: "plan_end_time",
        label: "完工时间",
        minWidth: 100,
        align: "center",
        headerAlign: "center",
        formatter: (row: ProduceWreportTable) => formatDateTimeTwoLines(row.plan_end_time),
      },
      {
        prop: "real_end_time",
        label: "实际时间",
        minWidth: 100,
        align: "center",
        headerAlign: "center",
        formatter: (row: ProduceWreportTable) => formatDateTimeTwoLines(row.real_end_time),
      },
      {
        prop: "plan_user_id",
        label: "执行用户",
        minWidth: 90,
        showOverflowTooltip: true,
        align: "center",
        formatter: (row: ProduceWreportTable) => {
          const u = userList.value.find((item) => item.id === row.plan_user_id);
          return row.plan_user_name || u?.name || u?.username || "—";
        },
      },
      {
        prop: "real_user_id",
        label: "实际用户",
        minWidth: 90,
        showOverflowTooltip: true,
        headerAlign: "center",
        visible: false,
        formatter: (row: ProduceWreportTable) => {
          const u = userList.value.find((item) => item.id === row.real_user_id);
          return row.real_user_name || u?.name || u?.username || "—";
        },
      },
      { prop: "description", label: "备注/描述", minWidth: 130, showOverflowTooltip: true, headerAlign: "center", visible: false },
      { prop: "created_time", label: "创建时间", width: 168, sortable: true, showOverflowTooltip: true, headerAlign: "center", visible: false },
      { prop: "updated_time", label: "更新时间", width: 168, sortable: true, showOverflowTooltip: true, headerAlign: "center", visible: false },
      {
        prop: "created_by",
        label: "创建人",
        minWidth: 80,
        headerAlign: "center",
        formatter: (row: ProduceWreportTable) => row.created_by?.name ?? "—",
        visible: false,
      },
      {
        prop: "updated_by",
        label: "更新人",
        minWidth: 80,
        headerAlign: "center",
        formatter: (row: ProduceWreportTable) => row.updated_by?.name ?? "—",
        visible: false,
      },
      {
        prop: "status",
        label: "状态",
        width: 85,
        fixed: "right",
        align: "center",
        headerAlign: "center",
        formatter: (row: ProduceWreportTable) => {
          const statusStr = String(row.status ?? "");
          const config = STATUS_CONFIG[statusStr];
          return h(
            ElTag,
            { type: config?.type ?? "info" },
            () => config?.text ?? (statusStr || "—")
          );
        },
      },
      {
        prop: "operation",
        label: "操作",
        width: 135,
        fixed: "right",
        align: "center",
        headerAlign: "center",
        formatter: (row: ProduceWreportTable) => formatOperationCell(row),
      },
    ],
  },
});

const crudCols = toCrudCols(columns);

const exportQueryParams = computed(() => {
  return stripPaginationParams(searchParams as Record<string, unknown>);
});

const importContentConfig = computed<IContentConfig>(() => ({
  permPrefix: "module_produce:produce_wreport",
  cols: crudCols.value,
  indexAction: async () => ({}),
  importTemplate: () => ProduceWreportAPI.downloadTemplateProduceWreport(),
}));

const exportContentConfig = computed(() => ({
  permPrefix: "module_produce:produce_wreport",
  cols: crudCols.value,
  exportsBlobAction: async (params: IObject) => {
    const merged = {
      ...(exportQueryParams.value as unknown as Record<string, unknown>),
      ...params,
    } as unknown as ProduceWreportPageQuery;
    const res = await ProduceWreportAPI.exportProduceWreport(merged);
    return res.data as Blob;
  },
}));

const { dialogVisible } = useCrudDialog();

const detailFormData = ref<ProduceWreportTable>({});

const detailItems: import("@/components/display/fa-descriptions/index.vue").DescriptionsItem[] = [
  { label: "单号", prop: "no" },
  { label: "所属项目", prop: "project_name" },
  { label: "所属部件", prop: "component_name" },
  { label: "数量", prop: "plan_count" },
  { label: "工艺", prop: "craft_name" },
  { label: "工时", prop: "man_hour" },
  { label: "完工时间", prop: "plan_end_time" },
  { label: "实际时间", prop: "real_end_time" },
  { label: "执行用户", prop: "plan_user_name" },
  { label: "实际用户", prop: "real_user_name" },
  { label: "状态", prop: "status", tag: { map: { "0": { type: "success", text: "启用" }, "1": { type: "danger", text: "禁用" }, "2": { type: "info", text: "待生产" }, "3": { type: "primary", text: "生产中" }, "4": { type: "success", text: "已完成" }, "5": { type: "danger", text: "已取消" }, "6": { type: "warning", text: "已暂停" } } } },
  { label: "备注/描述", prop: "description" },
  { label: "创建时间", prop: "created_time" },
  { label: "更新时间", prop: "updated_time" },
  { label: "创建人", prop: "created_by.name" },
  { label: "更新人", prop: "updated_by.name" },
];

const formData = ref<ProduceWreportForm>(createInitialFormData());

const projectList = ref<ProduceProjectTable[]>([]);
const projectLoading = ref(false);
const projectPage = ref(1);
const projectPageSize = 10;
const projectTotal = ref(0);
const totalProjectPages = computed(() => Math.ceil(projectTotal.value / projectPageSize));

const componentList = ref<ProduceComponentTable[]>([]);
const componentLoading = ref(false);
const componentPage = ref(1);
const componentPageSize = 10;
const componentTotal = ref(0);
const totalComponentPages = computed(() => Math.ceil(componentTotal.value / componentPageSize));

const craftList = ref<ProduceCraftTable[]>([]);
const craftLoading = ref(false);
const rootCraftList = computed(() => {
  return craftList.value.filter(
    (item) => !item.parent_id || (dialogVisible.type === "update" && item.id === formData.value.craft_id)
  );
});

const userList = ref<UserInfo[]>([]);
const userLoading = ref(false);

/** 当前选中的工艺对象 */
const selectedCraft = computed(() => {
  if (!formData.value.craft_id) return null;
  return craftList.value.find((c) => c.id === formData.value.craft_id) ?? null;
});

/** 当前选中的工艺关联的岗位ID */
const targetPositionId = computed(() => {
  return selectedCraft.value?.position_id ?? null;
});

/** 当前选中的工艺关联的岗位名称 */
const targetPositionName = computed(() => {
  return selectedCraft.value?.position_name ?? null;
});

/** 根据工艺岗位ID过滤出的执行用户列表 */
const filteredPlanUserList = computed(() => {
  if (!isSuperuser.value) {
    const me = userList.value.find((u) => u.id === currentUserId.value);
    if (me) return [me];
    if (currentUserId.value) {
      return [
        {
          id: currentUserId.value,
          name: userStore.info.name || "",
          username: userStore.info.username || "",
        } as UserInfo,
      ];
    }
    return [];
  }
  // 如果还没有选中工艺，则执行用户列表为空
  if (!formData.value.craft_id) {
    return [];
  }
  const posId = targetPositionId.value;
  if (!posId) {
    // 选了工艺但工艺未关联岗位，显示全部用户
    return userList.value;
  }
  // 过滤出拥有该岗位的人员
  const matched = userList.value.filter((u) => {
    return Array.isArray(u.position_ids) && u.position_ids.includes(posId);
  });

  // 编辑模式下，若已选中的用户不在该岗位中，保留该用户以保证回显正常
  if (
    formData.value.plan_user_id &&
    !matched.some((u) => u.id === formData.value.plan_user_id)
  ) {
    const current = userList.value.find((u) => u.id === formData.value.plan_user_id);
    if (current) {
      return [current, ...matched];
    }
  }

  return matched;
});

// 监听工艺切换：
// 1. 如果清空了工艺，自动清空执行用户
// 2. 当选中的工艺改变时，如果当前执行用户不符合新工艺的岗位，自动清空执行用户
watch(
  () => formData.value.craft_id,
  (newCraftId, oldCraftId) => {
    if (!isSuperuser.value) {
      formData.value.plan_user_id = currentUserId.value;
      return;
    }
    if (!newCraftId) {
      formData.value.plan_user_id = undefined;
      return;
    }
    if (newCraftId !== oldCraftId && formData.value.plan_user_id) {
      const posId = targetPositionId.value;
      if (posId) {
        const currentUser = userList.value.find((u) => u.id === formData.value.plan_user_id);
        const hasPosition = currentUser?.position_ids?.includes(posId);
        if (!hasPosition) {
          formData.value.plan_user_id = undefined;
        }
      }
    }
  }
);

let isGenerating = false;

async function handleGenerateNo() {
  if (isGenerating) return;
  isGenerating = true;
  try {
    const res = await ProduceWreportAPI.getProduceWreportList({
      page_no: 1,
      page_size: 1,
      order_by: JSON.stringify([{ id: "desc" }]),
    });
    const items = res.data?.data?.items;
    if (!items || items.length === 0) return;

    const lastNo = items[0]?.no;
    if (!lastNo || typeof lastNo !== "string") return;

    // 贪婪模式提取字符串末尾的纯数字
    const match = lastNo.match(/(\d+)$/);
    if (!match || match.index === undefined) return;

    const digits = match[1];
    const prefix = lastNo.slice(0, match.index);
    const a = (BigInt(digits) + 1n).toString().padStart(digits.length, "0");
    formData.value.no = `${prefix}${a}`;
  } catch {
    // 获取失败静默退出
  } finally {
    isGenerating = false;
  }
}

async function fetchProjectOptions(page = 1) {
  projectLoading.value = true;
  try {
    const res = await ProduceProjectAPI.getProduceProjectList({
      page_no: page,
      page_size: projectPageSize,
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

async function fetchComponentOptions(page = 1, projectId?: number) {
  const pId = projectId ?? formData.value.project_id;
  if (!pId) {
    componentList.value = [];
    componentTotal.value = 0;
    componentPage.value = 1;
    return;
  }
  componentLoading.value = true;
  try {
    const res = await ProduceComponentAPI.getProduceComponentList({
      project_id: pId,
      page_no: page,
      page_size: componentPageSize,
    });
    componentList.value = res.data.data?.items ?? [];
    componentTotal.value = res.data.data?.total ?? 0;
    componentPage.value = page;

    if (formData.value.component_id && !componentList.value.some((c) => c.id === formData.value.component_id)) {
      try {
        const detailRes = await ProduceComponentAPI.getProduceComponentDetail(formData.value.component_id);
        if (detailRes.data.data) {
          componentList.value = [detailRes.data.data, ...componentList.value];
        }
      } catch {
        // 忽略
      }
    }
  } catch (err) {
    if (import.meta.env.DEV) console.error("加载部件列表失败:", err);
  } finally {
    componentLoading.value = false;
  }
}

function handleComponentDropdownVisible(visible: boolean) {
  if (visible && componentList.value.length === 0 && formData.value.project_id) {
    fetchComponentOptions(1);
  }
}

async function handleProjectChange(val?: number) {
  formData.value.component_id = undefined;
  componentList.value = [];
  componentTotal.value = 0;
  componentPage.value = 1;
  if (val) {
    await fetchComponentOptions(1, val);
  }
}

async function loadCrafts() {
  craftLoading.value = true;
  try {
    const res = await ProduceCraftAPI.getProduceCraftList({ page_no: 1, page_size: 1000 });
    craftList.value = res.data.data?.items ?? [];
  } catch (err) {
    if (import.meta.env.DEV) console.error("加载工艺选项失败:", err);
  } finally {
    craftLoading.value = false;
  }
}

async function loadUsers() {
  userLoading.value = true;
  try {
    const res = await UserAPI.listUser({ page_no: 1, page_size: 1000 });
    userList.value = res.data.data?.items ?? [];
  } catch (err) {
    if (import.meta.env.DEV) console.error("加载用户列表失败:", err);
  } finally {
    userLoading.value = false;
  }
}

// 监听编辑态回显：若有 component_id 但无 project_id，反查部件获取所属 project_id 并加载该项目下的部件
watch(
  () => formData.value.component_id,
  async (newCompId) => {
    if (newCompId && !formData.value.project_id) {
      try {
        const res = await ProduceComponentAPI.getProduceComponentDetail(newCompId);
        const comp = res.data.data;
        if (comp?.project_id) {
          formData.value.project_id = comp.project_id;
          await fetchComponentOptions(1, comp.project_id);
        }
      } catch {
        // 忽略
      }
    }
  }
);

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
  loadCrafts();
  loadUsers();
});

const rules = reactive({
  no: [{ required: true, message: "请填写单号或点击生成", trigger: "blur" }],
  project_id: [{ required: true, message: "请选择所属项目", trigger: "change" }],
  component_id: [{ required: true, message: "请选择所属部件", trigger: "change" }],
  plan_count: [{ required: true, message: "请填写数量", trigger: "blur" }],
  craft_id: [{ required: true, message: "请选择工艺", trigger: "change" }],
  plan_end_time: [{ required: true, message: "请选择完工时间", trigger: "change" }],
  plan_user_id: [{ required: true, message: "请选择执行用户", trigger: "change" }],
  description: [{ required: false, message: "请填写备注/描述", trigger: "blur" }],
});

const dialogFormItems: FormItem[] = [
  { key: "no", label: "单号", type: "input" },
  { key: "project_id", label: "所属项目", type: "select" },
  { key: "component_id", label: "所属部件", type: "select" },
  { key: "plan_count", label: "数　　量", type: "number", props: { placeholder: "请输入数量", class: "w-full", style: { width: "100%" } } },
  { key: "craft_id", label: "工　　艺", type: "select" },
  { key: "plan_end_time", label: "完工时间", type: "datetime", props: { placeholder: "请选择完工时间", valueFormat: "YYYY-MM-DD HH:mm:ss", style: "width: 100%" } },
  { key: "plan_user_id", label: "执行用户", type: "select" },
  {
    key: "description",
    label: "描　　述",
    type: "input",
    props: {
      type: "textarea",
      rows: 3,
      maxlength: 100,
      showWordLimit: true,
      placeholder: "请输入描述",
    },
  },
];

const dataFormRef = ref<InstanceType<typeof FaForm> | null>(null);
const formRenderKey = ref(0);

const crud = useCrudForm<ProduceWreportForm>({
  formData,
  initialFormData: createInitialFormData(),
  dialogVisible,
  dataFormRef,
  formRenderKey,
  detailApi: (id: number) => ProduceWreportAPI.getProduceWreportDetail(id),
  createApi: (data: ProduceWreportForm) => {
    const { project_id, ...payload } = data;
    if (!isSuperuser.value && currentUserId.value) {
      payload.plan_user_id = currentUserId.value;
      payload.real_user_id = currentUserId.value;
    } else if (!payload.real_user_id && payload.plan_user_id) {
      payload.real_user_id = payload.plan_user_id;
    }
    if (payload.status === undefined) {
      payload.status = "2";
    }
    if (payload.man_hour === undefined) {
      payload.man_hour = 0;
    }
    return ProduceWreportAPI.createProduceWreport(payload);
  },
  updateApi: (id: number, data: ProduceWreportForm) => {
    const { project_id, ...payload } = data;
    if (!isSuperuser.value && currentUserId.value) {
      payload.plan_user_id = currentUserId.value;
    }
    return ProduceWreportAPI.updateProduceWreport(id, payload);
  },
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

const handleSearch = async (params: ProduceWreportSearchFormParams) => {
  await searchBarRef.value?.validate();
  replaceSearchParams({
    order_by: JSON.stringify([{ id: "desc" }]),
    no: params.no,
    component_id: params.component_id,
    craft_id: params.craft_id,
    plan_count: params.plan_count,
    real_count: params.real_count,
    plan_end_time: params.plan_end_time,
    real_end_time: params.real_end_time,
    plan_user_id: params.plan_user_id,
    real_user_id: params.real_user_id,
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
    no: undefined,
    component_id: undefined,
    craft_id: undefined,
    plan_count: undefined,
    real_count: undefined,
    plan_end_time: undefined,
    real_end_time: undefined,
    plan_user_id: undefined,
    real_user_id: undefined,
    status: undefined,
    created_id: undefined,
    updated_id: undefined,
    created_time: [],
    updated_time: [],
  };
  await resetSearchParams();
};

function buildRowActions(row: ProduceWreportTable): TableOperationAction[] {
  const isCompleted = String(row.status) === "4";
  const all: TableOperationAction[] = [
    {
      key: "detail",
      label: "详情",
      artType: "view",
      perm: "module_produce:produce_wreport:detail",
      run: () => void crud.handleOpenDialog("detail", row[PK] as number),
    },
    {
      key: "submit",
      label: "提交",
      artType: "edit",
      icon: "ri:check-line",
      iconColor: "#67c23a",
      perm: "module_produce:produce_wreport:update",
      disabled: isCompleted,
      run: () => handleSubmitRow(row),
    },
    {
      key: "delete",
      label: "删除",
      artType: "delete",
      icon: "ri:delete-bin-4-line",
      perm: "module_produce:produce_wreport:delete",
      run: () => deleteRow(row),
    },
  ];
  return all;
}

function formatOperationCell(row: ProduceWreportTable) {
  return renderTableOperationCell(buildRowActions(row), {
    wrapperClass: "inline-flex flex-wrap items-center justify-center gap-1.5 action-btn-group",
    tooltipPlacement: "left-start",
  });
}

async function handleAdd() {
  createLoading.value = true;
  try {
    await crud.handleOpenDialog("create");
    if (!isSuperuser.value && currentUserId.value) {
      formData.value.plan_user_id = currentUserId.value;
      formData.value.real_user_id = currentUserId.value;
    }
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

/** 提交工单（将状态变更为已完成） */
const handleSubmitRow = async (row: ProduceWreportTable) => {
  if (!row[PK]) return;
  if (String(row.status) === "4") {
    ElMessage.warning("该工单已是已完成状态，无需重复提交");
    return;
  }
  const projectName = row.project_name || "—";
  const componentName =
    row.component_name ||
    componentList.value.find((c) => c.id === row.component_id)?.name ||
    (row.component_id ? `部件#${row.component_id}` : "—");
  const orderNo = row.no || row[PK];

  try {
    await confirmAction(
      `确认将以下工单提交为已完成吗？
      单号：${orderNo}
      项目：${projectName}
      部件：${componentName}`,
      "提交确认"
    );
    await ProduceWreportAPI.updateProduceWreport(row[PK] as number, { status: "4" });
    ElMessage.success("工单提交成功，状态已变更为已完成");
    await refreshData();
  } catch {
    // 用户取消
  }
};

const deleteRow = async (row: ProduceWreportTable) => {
  if (!row[PK]) return;
  const projectName = row.project_name || "—";
  const componentName =
    row.component_name ||
    componentList.value.find((c) => c.id === row.component_id)?.name ||
    (row.component_id ? `部件#${row.component_id}` : "—");
  const orderNo = row.no || row[PK];

  try {
    await confirmDelete(
      `确定删除工单【${orderNo}】（项目：${projectName}，部件：${componentName}）吗？此操作不可恢复！`
    );
    await ProduceWreportAPI.deleteProduceWreport([row[PK] as number]);
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
    await ProduceWreportAPI.deleteProduceWreport(ids);
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
    await ProduceWreportAPI.batchProduceWreport({ ids, status });
    // 成功 / 失败提示由 axios 拦截器统一处理
    faTableRef.value?.elTableRef?.clearSelection();
    await refreshData();
  } catch {
    // 用户取消
  }
}

async function handleCrudImportUpload(formData: FormData) {
  try {
    const res = await ProduceWreportAPI.importProduceWreport(formData);
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

    // 详情、删除图标调整为精致小巧尺寸
    .fa-svg-icon {
      font-size: 16px !important;
      width: 16px !important;
      height: 16px !important;
    }
  }

  // 提交对号按钮适度调小并适配淡绿风格
  span:nth-child(2) .hover-btn {
    color: #67c23a !important;
    background-color: rgba(103, 194, 58, 0.12) !important;

    .fa-svg-icon {
      font-size: 18px !important;
      width: 18px !important;
      height: 18px !important;
    }

    &:hover {
      background-color: rgba(103, 194, 58, 0.22) !important;
      color: #529b2e !important;
    }
  }
}

:deep(.crud-dialog-art-form) {
  // 红色星号单独对齐，未设星号的行预留星号位置；保持中文等宽对齐
  .el-form-item__label {
    position: relative;
    display: inline-flex;
    align-items: center;
    justify-content: flex-start;
    padding-left: 14px !important;
    box-sizing: border-box;
    white-space: pre;

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

  // 表单文本与输入控件撑满
  .el-form-item__content {
    .el-input,
    .el-input-number,
    .el-select,
    .el-date-editor,
    .el-textarea,
    .custom-input-container {
      width: 100%;
    }
  }
}

// 表头的高度
:deep(.el-table__header th.el-table__cell) { padding: 7px 0 !important; }
// 整个表格卡片的上内边距
.fa-table-card :deep(.el-card__body) { padding-top: 10px; }
// 表格底部到分页区控件顶部的间距
:deep(.fa-table .pagination) { padding-top: 5px; }
// 调整整个表格卡片的下内边距
.fa-table-card :deep(.el-card__body) { padding-bottom: 10px; }

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

:deep(.craft-select-center) {
  // 整体外框容器：作为绝对定位的参照基准
  .el-select__wrapper {
    position: relative !important;
    padding: 0 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
  }

  // 右侧下拉箭头与清除图标：绝对定位浮于最右侧，不参与中心计算
  .el-select__suffix {
    position: absolute !important;
    right: 12px !important;
    top: 50% !important;
    transform: translateY(-50%) !important;
    margin: 0 !important;
    padding: 0 !important;
    z-index: 2;
  }

  // 内部选区容器：占满 100% 宽度，左右居中
  .el-select__selection {
    position: absolute !important;
    left: 0 !important;
    right: 0 !important;
    top: 0 !important;
    bottom: 0 !important;
    width: 100% !important;
    height: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    text-align: center !important;
  }

  // 选中的文本项：相对整个输入框外框满宽绝对居中
  .el-select__selected-item {
    position: absolute !important;
    left: 0 !important;
    right: 0 !important;
    top: 50% !important;
    transform: translateY(-50%) !important;
    width: 100% !important;
    margin: 0 auto !important;
    padding: 0 32px !important; // 预留右侧按钮空间，文字溢出时省略
    box-sizing: border-box !important;
    text-align: center !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    pointer-events: none;

    span {
      display: inline-block !important;
      text-align: center !important;
      margin: 0 auto !important;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
  }

  // 占位提示语（“请选择工艺”）：相对整个输入框外框满宽绝对居中
  .el-select__placeholder {
    position: absolute !important;
    left: 0 !important;
    right: 0 !important;
    top: 50% !important;
    transform: translateY(-50%) !important;
    width: 100% !important;
    margin: 0 auto !important;
    padding: 0 32px !important;
    box-sizing: border-box !important;
    text-align: center !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    pointer-events: none;

    span {
      display: inline-block !important;
      text-align: center !important;
      margin: 0 auto !important;
    }
  }

  // 搜索输入框与光标：满宽居中
  .el-select__input-wrapper {
    position: absolute !important;
    left: 0 !important;
    right: 0 !important;
    top: 50% !important;
    transform: translateY(-50%) !important;
    width: 100% !important;
    margin: 0 auto !important;
    padding: 0 32px !important;
    box-sizing: border-box !important;
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    text-align: center !important;
  }

  .el-select__input,
  .el-input__inner,
  input {
    text-align: center !important;
    margin: 0 auto !important;
    width: 100% !important;
  }
}

</style>
