<template>
  <ElRow :gutter="16">
    <ElCol v-for="item in dataList" :key="item.des" :sm="12" :md="8" :lg="8" class="mb-5">
      <div
        class="fa-card relative flex flex-col justify-center h-30 px-5 cursor-pointer transition-all duration-300 hover:shadow-md hover:-translate-y-0.5"
        @click="handleCardClick(item)"
      >
        <div class="flex items-center justify-between">
          <span class="text-sm font-medium text-g-600">{{ item.des }}</span>
          <ElTag v-if="item.tag" :type="item.tagType || 'info'" size="small" effect="light">
            {{ item.tag }}
          </ElTag>
        </div>

        <div class="flex items-center justify-between mt-2">
          <div class="flex items-center gap-2">
            <FaCountTo class="text-lg font-medium" :target="item.num" :duration="1300" />
            <span v-if="item.status" class="text-xs flex items-center gap-1" :class="item.statusColor || 'text-success'">
              <ElIcon v-if="item.statusIcon"><component :is="item.statusIcon" /></ElIcon>
              {{ item.status }}
            </span>
          </div>
          <div
            v-if="item.icon"
            class="size-10 rounded-xl flex items-center justify-center transition-transform duration-300 group-hover:scale-105"
            :class="item.iconBg || 'bg-theme/10'"
          >
            <FaSvgIcon
              :icon="item.icon"
              class="text-xl"
              :class="[
                item.iconColor || 'text-theme',
                item.animateIcon ? 'animate-[spin_4s_linear_infinite]' : '',
              ]"
            />
          </div>
        </div>

        <div class="flex items-center justify-between mt-1 text-xs text-g-600">
          <br><br>
          <span>
            {{ item.totalLabel }}：<span class="font-medium text-g-800">{{ item.totalValue }}</span>
          </span>
          <!-- <span v-if="item.updateTime">{{ item.updateTime }}</span> -->
        </div>
      </div>
    </ElCol>
  </ElRow>
</template>

<script setup lang="ts">
import { ref, onMounted, markRaw, computed, type Component } from "vue";
import { useRouter } from "vue-router";
import { Timer, Tools, CircleCheck } from "@element-plus/icons-vue";
import { useUserStore } from "@stores";
import ProduceWorderAPI from "@/api/module_produce/produce_worder";

interface CardDataItem {
  des: string;
  icon: string;
  iconBg?: string;
  iconColor?: string;
  animateIcon?: boolean;
  num: number;
  tag?: string;
  tagType?: "danger" | "success" | "warning" | "info" | "primary";
  status?: string;
  statusColor?: string;
  statusIcon?: Component;
  totalLabel?: string;
  totalValue?: string;
  updateTime?: string;
  statusCode: string;
}

const router = useRouter();
const userStore = useUserStore();

const now = new Date();
const pad = (n: number) => String(n).padStart(2, "0");
const timeStr = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())} ${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`;

const dataList = ref<CardDataItem[]>([
  {
    des: "待生产工单",
    icon: "ri:time-line",
    iconBg: "bg-warning/10",
    iconColor: "text-warning",
    num: 0,
    // tag: "待生产",
    tagType: "warning",
    // status: "待生产",
    statusColor: "text-warning",
    statusIcon: markRaw(Timer),
    totalLabel: "统计范围",
    totalValue: "加载中...",
    updateTime: timeStr,
    statusCode: "2",
  },
  {
    des: "生产中工单",
    icon: "ri:loader-2-line",
    iconBg: "bg-primary/10",
    iconColor: "text-primary",
    animateIcon: true,
    num: 0,
    // tag: "生产中",
    tagType: "primary",
    // status: "生产中",
    statusColor: "text-primary",
    statusIcon: markRaw(Tools),
    totalLabel: "统计范围",
    totalValue: "加载中...",
    updateTime: timeStr,
    statusCode: "3",
  },
  {
    des: "已完成工单",
    icon: "ri:checkbox-circle-line",
    iconBg: "bg-success/10",
    iconColor: "text-success",
    num: 0,
    // tag: "已完成",
    tagType: "success",
    // status: "已完成",
    statusColor: "text-success",
    statusIcon: markRaw(CircleCheck),
    totalLabel: "统计范围",
    totalValue: "加载中...",
    updateTime: timeStr,
    statusCode: "4",
  },
]);

/**
 * 判断当前用户是否为超管、管理员或生产经理
 */
const isManagerOrAdmin = computed(() => {
  const info = userStore.info;
  if (info?.is_superuser) return true;

  const targetKeywords = ["管理员", "经理"];
  const targetCodes = ["SUPER_ADMIN", "ADMIN", "MANAGER", "PRODUCTION_MANAGER"];

  // 1. 检查角色
  const roles = info?.roles || [];
  const hasRole = roles.some((r) => {
    const nameMatch = r.name && targetKeywords.some((kw) => r.name?.includes(kw));
    const codeMatch =
      r.code &&
      (targetCodes.includes(r.code.toUpperCase()) ||
        r.code.toUpperCase().includes("MANAGER") ||
        r.code.toUpperCase().includes("ADMIN"));
    return nameMatch || codeMatch;
  });
  if (hasRole) return true;

  if (info?.role_names?.some((name) => targetKeywords.some((kw) => name.includes(kw)))) {
    return true;
  }

  // 2. 检查岗位（如岗位为“生产经理”）
  const positions = (info as any)?.positions || [];
  const hasPosition = positions.some((p: any) => {
    const nameMatch = p.name && targetKeywords.some((kw) => p.name?.includes(kw));
    const codeMatch =
      p.code &&
      (targetCodes.includes(p.code.toUpperCase()) ||
        p.code.toUpperCase().includes("MANAGER") ||
        p.code.toUpperCase().includes("ADMIN"));
    return nameMatch || codeMatch;
  });
  if (hasPosition) return true;

  // 3. 检查工时核算员（角色为“工时”且岗位为“工时核算员”，或岗位为“工时核算员”）
  const hasHourRole =
    roles.some(
      (r) =>
        (r.name && r.name.includes("工时")) ||
        (r.code && ["MAN_HOUR", "WORK_HOUR"].includes(r.code.toUpperCase()))
    ) || info?.role_names?.some((name) => name.includes("工时"));

  const hasHourPosition = positions.some(
    (p: any) =>
      (p.name && (p.name.includes("工时核算员") || p.name.includes("核算员"))) ||
      (p.code && p.code.toUpperCase().includes("HOURS_CALCULATOR"))
  );

  if ((hasHourRole && hasHourPosition) || hasHourPosition) {
    return true;
  }

  return false;
});

/**
 * 点击卡片跳转至工单管理并过滤对应状态
 */
function handleCardClick(item: CardDataItem) {
  try {
    router.push({
      path: "/produce/produce_worder",
      query: { status: item.statusCode },
    });
  } catch {
    // 忽略跳转错误
  }
}

/**
 * 更新卡片数据
 */
function applyStats(pending: number, producing: number, completed: number, isManager: boolean) {
  const now2 = new Date();
  const ts = `${now2.getFullYear()}-${pad(now2.getMonth() + 1)}-${pad(now2.getDate())} ${pad(now2.getHours())}:${pad(now2.getMinutes())}:${pad(now2.getSeconds())}`;
  const scopeText = isManager ? "全部工单" : "我的工单";

  dataList.value[0]!.num = pending;
  dataList.value[0]!.totalValue = scopeText;
  dataList.value[0]!.updateTime = ts;

  dataList.value[1]!.num = producing;
  dataList.value[1]!.totalValue = scopeText;
  dataList.value[1]!.updateTime = ts;

  dataList.value[2]!.num = completed;
  dataList.value[2]!.totalValue = scopeText;
  dataList.value[2]!.updateTime = ts;
}

/**
 * 前端降级统计：利用已有分页列表接口查各状态数量
 */
async function fallbackLoadStats() {
  const isManager = isManagerOrAdmin.value;
  const currentUserId = userStore.info?.id;

  const queryBase = isManager ? {} : { plan_user_id: currentUserId };

  try {
    const [res2, res3, res4] = await Promise.allSettled([
      ProduceWorderAPI.getProduceWorderList({ page_no: 1, page_size: 1, status: "2", ...queryBase }),
      ProduceWorderAPI.getProduceWorderList({ page_no: 1, page_size: 1, status: "3", ...queryBase }),
      ProduceWorderAPI.getProduceWorderList({ page_no: 1, page_size: 1, status: "4", ...queryBase }),
    ]);

    const pending = res2.status === "fulfilled" ? (res2.value.data?.data?.total ?? 0) : 0;
    const producing = res3.status === "fulfilled" ? (res3.value.data?.data?.total ?? 0) : 0;
    const completed = res4.status === "fulfilled" ? (res4.value.data?.data?.total ?? 0) : 0;

    applyStats(pending, producing, completed, isManager);
  } catch {
    // 接口错误时不影响页面
  }
}

/**
 * 加载统计数据
 */
async function loadStats() {
  try {
    const { data: res } = await ProduceWorderAPI.getDashboardStats();
    if (res?.data) {
      applyStats(
        res.data.pending_count ?? 0,
        res.data.producing_count ?? 0,
        res.data.completed_count ?? 0,
        res.data.is_manager ?? false
      );
      return;
    }
  } catch {
    // 后端统计接口失败时降级
  }

  await fallbackLoadStats();
}

onMounted(() => {
  loadStats();
});
</script>

<style scoped>
</style>
