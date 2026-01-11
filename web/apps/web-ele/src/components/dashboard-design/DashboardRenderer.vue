<script setup lang="ts">
import type { DashboardConfig } from './store/dashboardDesignStore';

/**
 * 仪表盘渲染器
 * 用于在实际页面中展示设计好的仪表盘配置
 */
import { computed, onMounted, ref, watch } from 'vue';

import { $t } from '@vben/locales';

import { ElEmpty, ElScrollbar } from 'element-plus';
import { GridItem, GridLayout } from 'grid-layout-plus';

import WidgetRenderer from './components/WidgetRenderer.vue';

const props = defineProps<{
  // 仪表盘配置 JSON 字符串或对象
  config: DashboardConfig | string;
}>();

// 解析后的配置
const dashboardConfig = ref<DashboardConfig | null>(null);

// 解析配置
const parseConfig = () => {
  if (!props.config) {
    dashboardConfig.value = null;
    return;
  }

  if (typeof props.config === 'string') {
    try {
      dashboardConfig.value = JSON.parse(props.config);
    } catch {
      console.error('Invalid dashboard config JSON');
      dashboardConfig.value = null;
    }
  } else {
    dashboardConfig.value = props.config;
  }
};

onMounted(parseConfig);
watch(() => props.config, parseConfig);

// 布局数据
const layout = computed(() => {
  if (!dashboardConfig.value) return [];
  return dashboardConfig.value.widgets.map((w) => ({
    i: w.i,
    x: w.x,
    y: w.y,
    w: w.w,
    h: w.h,
  }));
});

// 获取 widget 配置
const getWidget = (i: string) => {
  if (!dashboardConfig.value) return null;
  return dashboardConfig.value.widgets.find((w) => w.i === i);
};

// 获取动画延迟（交错入场效果）
const getAnimationDelay = (i: string) => {
  if (!dashboardConfig.value) return 0;
  const index = dashboardConfig.value.widgets.findIndex((w) => w.i === i);
  return index * 80; // 每个组件延迟 80ms
};
</script>

<template>
  <ElScrollbar
    class="dashboard-renderer h-full"
    :style="{ backgroundColor: dashboardConfig?.backgroundColor || '' }"
  >
    <div v-if="dashboardConfig && layout.length > 0">
      <GridLayout
        :layout="layout"
        :col-num="dashboardConfig.columns"
        :row-height="dashboardConfig.rowHeight"
        :margin="dashboardConfig.margin"
        :is-draggable="false"
        :is-resizable="false"
        :vertical-compact="true"
        :use-css-transforms="true"
        :style="
          dashboardConfig.showOuterMargin
            ? {}
            : {
                marginLeft: `-${dashboardConfig.margin[0]}px`,
                marginRight: `-${dashboardConfig.margin[0]}px`,
                marginTop: `-${dashboardConfig.margin[1]}px`,
                width: `calc(100% + ${dashboardConfig.margin[0] * 2}px)`,
              }
        "
      >
        <GridItem
          v-for="item in layout"
          :key="item.i"
          :i="item.i"
          :x="item.x"
          :y="item.y"
          :w="item.w"
          :h="item.h"
          class="dashboard-widget"
        >
          <WidgetRenderer
            v-if="getWidget(item.i)"
            :widget="getWidget(item.i)!"
            :is-design-mode="false"
            :animation-delay="getAnimationDelay(item.i)"
          />
        </GridItem>
      </GridLayout>
    </div>

    <ElEmpty v-else :description="$t('dashboard-design.noConfigTip')" class="py-20" />
  </ElScrollbar>
</template>

<style scoped>
.dashboard-renderer {
  background-color: var(--el-bg-color-page);
}

.dashboard-widget {
  overflow: hidden;
  background: var(--el-bg-color);
  border-radius: 8px;
  box-shadow: 0 1px 3px rgb(0 0 0 / 10%);
}
</style>
