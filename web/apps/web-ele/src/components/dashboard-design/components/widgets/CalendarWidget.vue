<script setup lang="ts">
import type { DashboardWidget } from '../../store/dashboardDesignStore';

import { ref } from 'vue';

import { Calendar } from '@vben/icons';

import { ElCalendar } from 'element-plus';

defineProps<{
  widget: DashboardWidget;
}>();

const selectedDate = ref(new Date());
</script>

<template>
  <div class="calendar-widget flex h-full flex-col p-3">
    <div class="mb-2 flex items-center gap-2">
      <Calendar class="text-muted-foreground h-4 w-4" />
      <span class="text-muted-foreground text-sm font-medium">{{
        widget.props.title
      }}</span>
    </div>
    <div class="min-h-0 flex-1 overflow-hidden">
      <ElCalendar v-model="selectedDate" class="compact-calendar" />
    </div>
  </div>
</template>

<style scoped>
/* 背景色由 WidgetRenderer 控制 */

.compact-calendar {
  --el-calendar-border: none;
}

:deep(.el-calendar) {
  height: 100%;
}

:deep(.el-calendar__header) {
  padding: 8px 0;
}

:deep(.el-calendar__body) {
  padding: 0;
}

:deep(.el-calendar-table thead th) {
  padding: 4px 0;
  font-size: 12px;
}

:deep(.el-calendar-table .el-calendar-day) {
  height: 32px;
  padding: 2px;
  font-size: 12px;
}

:deep(.el-calendar-table td.is-selected .el-calendar-day) {
  color: white;
  background-color: var(--el-color-primary);
  border-radius: 4px;
}

:deep(.el-calendar-table td.is-today .el-calendar-day) {
  font-weight: bold;
  color: var(--el-color-primary);
}
</style>
