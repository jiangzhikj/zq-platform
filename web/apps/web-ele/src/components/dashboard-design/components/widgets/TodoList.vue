<script setup lang="ts">
import { $t } from '@vben/locales';

import type { DashboardWidget } from '../../store/dashboardDesignStore';

import { CheckSquare } from '@vben/icons';

import { ElCheckbox, ElScrollbar, ElTag } from 'element-plus';

defineProps<{
  widget: DashboardWidget;
}>();

const getPriorityType = (priority: string) => {
  switch (priority) {
    case 'high': {
      return 'danger';
    }
    case 'low': {
      return 'info';
    }
    case 'medium': {
      return 'warning';
    }
    default: {
      return 'info';
    }
  }
};

const getPriorityLabel = (priority: string) => {
  switch (priority) {
    case 'high': {
      return $t('dashboard-design.widgets.todo.priority.high');
    }
    case 'low': {
      return $t('dashboard-design.widgets.todo.priority.low');
    }
    case 'medium': {
      return $t('dashboard-design.widgets.todo.priority.medium');
    }
    default: {
      return priority;
    }
  }
};
</script>

<template>
  <div class="todo-list flex h-full flex-col p-3">
    <div class="mb-3 flex items-center gap-2">
      <CheckSquare class="text-muted-foreground h-4 w-4" />
      <span class="text-muted-foreground text-sm font-medium">{{
        widget.props.title
      }}</span>
    </div>
    <ElScrollbar class="flex-1">
      <div class="space-y-2">
        <div
          v-for="item in widget.props.items"
          :key="item.id"
          class="flex items-center gap-2 rounded-md p-2 transition-colors hover:bg-gray-50 dark:hover:bg-gray-800"
        >
          <ElCheckbox :model-value="item.done" size="small" />
          <span
            class="flex-1 text-sm"
            :class="{ 'text-muted-foreground line-through': item.done }"
          >
            {{ item.title }}
          </span>
          <ElTag :type="getPriorityType(item.priority)" size="small">
            {{ getPriorityLabel(item.priority) }}
          </ElTag>
        </div>
      </div>
    </ElScrollbar>
  </div>
</template>

<style scoped>
/* 背景色由 WidgetRenderer 控制 */
</style>
