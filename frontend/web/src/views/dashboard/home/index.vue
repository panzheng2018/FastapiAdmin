<template>
  <div class="flex flex-col relative last:mb-0">
    <FaDashboardSkeleton v-if="loading" />
    <template v-else>
      <!-- 左列：主内容区 | 右列：侧边栏 -->
      <ElRow :gutter="20">
        <ElCol :xs="24" :md="18">

          <ElRow :gutter="20">
            <ElCol :xs="24" :md="16">
              <ElRow :gutter="20">
                <ElCol :xs="24" :sm="24" :md="24">
                  <CardList />
                </ElCol>
                <ElCol :xs="24" :sm="24" :md="24">
                  <WorderCardList />
                </ElCol>
              </ElRow>

            </ElCol>

          </ElRow>
        </ElCol>

        <ElCol :xs="24" :md="6" class="flex flex-col gap-5">
          <FaDataListCard
            class="mb-5"
            :maxCount="4"
            :list="healthList"
            title="系统健康"
            subtitle="实时 · 30s"
            :showMoreButton="true"
            @more="handleMore"
          />
        </ElCol>
      </ElRow>

    </template>
  </div>
</template>

<script setup lang="ts">
defineOptions({ name: "Home", inheritAttrs: false });

import { ref, onMounted, defineAsyncComponent } from "vue";
import { ElMessage } from "element-plus";
import { getDashboardMock } from "@/mock/dashboard";
import CardList from "./modules/card-list.vue";
import WorderCardList from "./modules/worder-card-list.vue";
const mock = getDashboardMock();
const loading = ref(false);
const healthList = ref(mock.health);
const timelineData = ref(mock.timeline);

onMounted(() => {
  // 后续替换为真实接口:
  // const { data } = await DashboardAPI.getStats();
  // 并删除 getDashboardMock() 调用
});

// 图表组件异步导入，减少首屏 echarts 加载
const FaLineChartCard = defineAsyncComponent(
  () => import("@/components/cards/fa-line-chart-card/index.vue")
);
const FaBarChartCard = defineAsyncComponent(
  () => import("@/components/cards/fa-bar-chart-card/index.vue")
);
const FaDonutChartCard = defineAsyncComponent(
  () => import("@/components/cards/fa-donut-chart-card/index.vue")
);

const FaTimelineListCard = defineAsyncComponent(
  () => import("@/components/cards/fa-timeline-list-card/index.vue")
);

function handleMore() {
  ElMessage.info("查看更多");
}
</script>
