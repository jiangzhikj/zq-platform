<script setup lang="ts">
import { $t } from '@vben/locales';

import type { DashboardWidget } from '../../store/dashboardDesignStore';

import { Award } from '@vben/icons';

import { ElScrollbar } from 'element-plus';

defineProps<{
  widget: DashboardWidget;
}>();

const getRankClass = (rank: number) => {
  switch (rank) {
    case 1: {
      return 'bg-yellow-500 text-white';
    }
    case 2: {
      return 'bg-gray-400 text-white';
    }
    case 3: {
      return 'bg-amber-600 text-white';
    }
    default: {
      return 'bg-gray-200 text-gray-600 dark:bg-gray-700 dark:text-gray-300';
    }
  }
};

const formatValue = (value: number) => {
  if (value >= 10_000) {
    return `${(value / 10_000).toFixed(1)}${$t('dashboard-design.widgets.ranking.tenThousand')}`;
  }
  return value.toLocaleString();
};
</script>

<template>
  <div class="ranking-list flex h-full flex-col p-3">
    <div class="mb-3 flex items-center gap-2">
      <Award class="text-muted-foreground h-4 w-4" />
      <span class="text-muted-foreground text-sm font-medium">{{
        widget.props.title
      }}</span>
    </div>
    <ElScrollbar class="flex-1">
      <div class="space-y-2">
        <div
          v-for="item in widget.props.items"
          :key="item.rank"
          class="flex items-center gap-3 rounded-md p-2 transition-colors hover:bg-gray-50 dark:hover:bg-gray-800"
        >
          <div
            class="flex h-6 w-6 flex-shrink-0 items-center justify-center rounded text-xs font-medium"
            :class="getRankClass(item.rank)"
          >
            {{ item.rank }}
          </div>
          <div class="flex-1 truncate text-sm">{{ item.name }}</div>
          <div class="text-muted-foreground text-sm font-medium">
            {{ formatValue(item.value) }}
          </div>
        </div>
      </div>
    </ElScrollbar>
  </div>
</template>

<style scoped>
/* 背景色由 WidgetRenderer 控制 */
</style>
