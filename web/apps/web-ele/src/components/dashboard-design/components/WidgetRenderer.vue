<script setup lang="ts">
import type {
  DashboardWidget,
  WidgetMaterial,
} from '../store/dashboardDesignStore';

import {
  computed,
  defineAsyncComponent,
  onMounted,
  onUnmounted,
  ref,
  watch,
} from 'vue';

import { Loader2 } from '@vben/icons';
import { $t } from '@vben/locales';

import { defaultWidgetStyle } from '../store/dashboardDesignStore';
import { createRefreshTimer, fetchWidgetData } from '../utils/dataFetcher';

const props = defineProps<{
  animationDelay?: number; // 入场动画延迟（毫秒）
  isDesignMode?: boolean;
  material?: WidgetMaterial;
  widget: DashboardWidget;
}>();

// 入场动画状态
const isEntered = ref(false);
// 数据更新动画状态
const isUpdating = ref(false);

// 组件映射
const widgetComponents: Record<
  string,
  ReturnType<typeof defineAsyncComponent>
> = {
  'stat-card': defineAsyncComponent(() => import('./widgets/StatCard.vue')),
  'progress-card': defineAsyncComponent(
    () => import('./widgets/ProgressCard.vue'),
  ),
  'chart-line': defineAsyncComponent(() => import('./widgets/ChartLine.vue')),
  'chart-bar': defineAsyncComponent(() => import('./widgets/ChartBar.vue')),
  'chart-pie': defineAsyncComponent(() => import('./widgets/ChartPie.vue')),
  'chart-gauge': defineAsyncComponent(() => import('./widgets/ChartGauge.vue')),
  'chart-area': defineAsyncComponent(() => import('./widgets/ChartArea.vue')),
  'chart-radar': defineAsyncComponent(() => import('./widgets/ChartRadar.vue')),
  'chart-funnel': defineAsyncComponent(
    () => import('./widgets/ChartFunnel.vue'),
  ),
  'chart-scatter': defineAsyncComponent(
    () => import('./widgets/ChartScatter.vue'),
  ),
  'chart-ring': defineAsyncComponent(() => import('./widgets/ChartRing.vue')),
  'chart-heatmap': defineAsyncComponent(
    () => import('./widgets/ChartHeatmap.vue'),
  ),
  'chart-kline': defineAsyncComponent(() => import('./widgets/ChartKline.vue')),
  'chart-sankey': defineAsyncComponent(
    () => import('./widgets/ChartSankey.vue'),
  ),
  'todo-list': defineAsyncComponent(() => import('./widgets/TodoList.vue')),
  'notice-list': defineAsyncComponent(() => import('./widgets/NoticeList.vue')),
  'ranking-list': defineAsyncComponent(
    () => import('./widgets/RankingList.vue'),
  ),
  'announcement-list': defineAsyncComponent(
    () => import('./widgets/AnnouncementList.vue'),
  ),
  'quick-links': defineAsyncComponent(() => import('./widgets/QuickLinks.vue')),
  'welcome-card': defineAsyncComponent(
    () => import('./widgets/WelcomeCard.vue'),
  ),
  calendar: defineAsyncComponent(() => import('./widgets/CalendarWidget.vue')),
  countdown: defineAsyncComponent(
    () => import('./widgets/CountdownWidget.vue'),
  ),
  clock: defineAsyncComponent(() => import('./widgets/ClockWidget.vue')),
  weather: defineAsyncComponent(() => import('./widgets/WeatherWidget.vue')),
  'image-carousel': defineAsyncComponent(
    () => import('./widgets/ImageCarousel.vue'),
  ),
  'data-table': defineAsyncComponent(() => import('./widgets/DataTable.vue')),
  iframe: defineAsyncComponent(() => import('./widgets/IframeWidget.vue')),
  'video-player': defineAsyncComponent(
    () => import('./widgets/VideoPlayer.vue'),
  ),
  image: defineAsyncComponent(() => import('./widgets/ImageWidget.vue')),
};

const currentComponent = computed(() => {
  return widgetComponents[props.widget.type];
});

// 动态数据
const dynamicProps = ref<Record<string, any>>({});
const isLoading = ref(false);
const hasError = ref(false);

// 合并后的 widget（静态 props + 动态 props）
const mergedWidget = computed(() => {
  return {
    ...props.widget,
    props: {
      ...props.widget.props,
      ...dynamicProps.value,
    },
  };
});

// 计算样式（只应用容器级别的样式，不影响组件内部）
const widgetStyle = computed(() => {
  const style = { ...defaultWidgetStyle, ...props.widget.style };
  const css: Record<string, string> = {};

  // 背景（默认使用主题背景色）
  css.backgroundColor = style.backgroundColor || 'var(--el-bg-color)';

  // 边框
  if (style.borderWidth && style.borderWidth > 0) {
    css.borderWidth = `${style.borderWidth}px`;
    css.borderStyle = style.borderStyle || 'solid';
    css.borderColor = style.borderColor || 'var(--el-border-color)';
  }

  // 圆角
  if (style.borderRadius !== undefined) {
    css.borderRadius = `${style.borderRadius}px`;
  }

  // 阴影
  if (style.shadowEnabled) {
    const color = style.shadowColor || 'rgba(0, 0, 0, 0.1)';
    const blur = style.shadowBlur || 4;
    const x = style.shadowOffsetX || 0;
    const y = style.shadowOffsetY || 1;
    css.boxShadow = `${x}px ${y}px ${blur}px ${color}`;
  } else {
    css.boxShadow = 'none';
  }

  return css;
});

// 加载数据
const loadData = async () => {
  console.log('[WidgetRenderer] loadData called', {
    type: props.widget.type,
    dataSource: props.widget.dataSource,
  });

  if (!props.widget.dataSource || props.widget.dataSource.type === 'static') {
    dynamicProps.value = {};
    return;
  }

  isLoading.value = true;
  hasError.value = false;

  try {
    const result = await fetchWidgetData(
      props.widget.dataSource,
      props.widget.props,
    );
    console.log('[WidgetRenderer] fetchWidgetData result', result);

    // 数据更新动画
    if (isEntered.value && Object.keys(dynamicProps.value).length > 0) {
      isUpdating.value = true;
      setTimeout(() => {
        isUpdating.value = false;
      }, 300);
    }

    dynamicProps.value = result.props;
  } catch (error) {
    console.error('[WidgetRenderer] loadData error', error);
    hasError.value = true;
  } finally {
    isLoading.value = false;
  }
};

// 刷新定时器清理函数
let cleanupTimer: (() => void) | null = null;

// 设置刷新定时器
const setupRefreshTimer = () => {
  if (cleanupTimer) {
    cleanupTimer();
    cleanupTimer = null;
  }

  // 支持 api 和 dataSource 类型的自动刷新
  const dsType = props.widget.dataSource?.type;
  if (!props.isDesignMode && (dsType === 'api' || dsType === 'dataSource')) {
    cleanupTimer = createRefreshTimer(props.widget.dataSource, loadData);
  }
};

// 监听数据源变化
watch(
  () => props.widget.dataSource,
  () => {
    loadData();
    setupRefreshTimer();
  },
  { deep: true },
);

onMounted(() => {
  loadData();
  setupRefreshTimer();

  // 入场动画
  const delay = props.animationDelay || 0;
  setTimeout(() => {
    isEntered.value = true;
  }, delay);
});

onUnmounted(() => {
  if (cleanupTimer) {
    cleanupTimer();
  }
});

// 动画类名
const animationClass = computed(() => {
  return {
    'widget-enter': true,
    'widget-entered': isEntered.value,
    'widget-updating': isUpdating.value,
  };
});
</script>

<template>
  <div
    class="widget-renderer relative h-full w-full overflow-hidden"
    :class="animationClass"
    :style="widgetStyle"
  >
    <!-- 加载状态 -->
    <div
      v-if="isLoading"
      class="absolute inset-0 z-10 flex items-center justify-center bg-white/50"
    >
      <Loader2 class="text-primary h-6 w-6 animate-spin" />
    </div>

    <!-- 错误状态 -->
    <div v-if="hasError && !isLoading" class="absolute right-2 top-2 z-10">
      <span class="text-xs text-red-500">{{ $t('dashboard-design.loadDataError') }}</span>
    </div>

    <!-- 组件内容 -->
    <component
      :is="currentComponent"
      v-if="currentComponent"
      :widget="mergedWidget"
      :is-design-mode="isDesignMode"
    />
    <div
      v-else
      class="flex h-full w-full items-center justify-center text-gray-400"
    >
      {{ $t('dashboard-design.unknownWidget') }}: {{ widget.type }}
    </div>
  </div>
</template>

<style scoped>
@keyframes pulse-update {
  0% {
    transform: scale(1);
  }

  50% {
    box-shadow: 0 0 0 2px var(--el-color-primary-light-5);
    transform: scale(1.02);
  }

  100% {
    transform: scale(1);
  }
}

.widget-enter {
  opacity: 0;
  transform: translateY(20px) scale(0.95);
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.widget-entered {
  opacity: 1;
  transform: translateY(0) scale(1);
}

/* 数据更新动画 */
.widget-updating {
  animation: pulse-update 0.3s ease-in-out;
}

/* 入场动画 */
</style>
