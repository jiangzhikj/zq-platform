<script setup lang="ts">
import { $t } from '@vben/locales';

import type { DashboardWidget } from '../../store/dashboardDesignStore';

import { computed } from 'vue';

import {
  Activity,
  Award,
  Bell,
  CreditCard,
  TrendingUp,
  Users,
} from '@vben/icons';

const props = defineProps<{
  showTitle?: boolean;
  widget: DashboardWidget;
}>();

// 图标映射
const iconMap: Record<string, any> = {
  TrendingUp,
  CreditCard,
  Users,
  Activity,
  Bell,
  Award,
};

const iconComponent = computed(() => {
  return iconMap[props.widget.props.iconName] || TrendingUp;
});

const trendClass = computed(() => {
  const trend = props.widget.props.trend || 0;
  if (trend > 0) return 'text-green-500';
  if (trend < 0) return 'text-red-500';
  return 'text-gray-500';
});

const trendIcon = computed(() => {
  const trend = props.widget.props.trend || 0;
  if (trend > 0) return '↑';
  if (trend < 0) return '↓';
  return '';
});

const formatValue = (value: number) => {
  if (value >= 10_000) {
    return `${(value / 10_000).toFixed(1)}${$t('dashboard-design.widgets.ranking.tenThousand')}`;
  }
  return value.toLocaleString();
};
</script>

<template>
  <div class="stat-card flex h-full flex-col justify-between p-4">
    <div class="flex items-start justify-between">
      <div>
        <div class="text-muted-foreground text-sm">
          {{ widget.props.title }}
        </div>
        <div class="mt-2 text-2xl font-bold">
          {{ widget.props.prefix }}{{ formatValue(widget.props.value)
          }}{{ widget.props.suffix }}
        </div>
      </div>
      <div
        class="flex h-10 w-10 items-center justify-center rounded-lg"
        :style="{ backgroundColor: `${widget.props.iconColor}20` }"
      >
        <component
          :is="iconComponent"
          class="h-5 w-5"
          :style="{ color: widget.props.iconColor }"
        />
      </div>
    </div>
    <div class="mt-3 flex items-center gap-1 text-sm">
      <span :class="trendClass">
        {{ trendIcon }} {{ Math.abs(widget.props.trend || 0) }}%
      </span>
      <span class="text-muted-foreground">{{ widget.props.trendLabel }}</span>
    </div>
  </div>
</template>

<style scoped>
/* 背景色由 WidgetRenderer 控制 */
</style>
