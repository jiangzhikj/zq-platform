<script setup lang="ts">
import type { DashboardWidget } from '../../store/dashboardDesignStore';

import { ElProgress } from 'element-plus';

defineProps<{
  widget: DashboardWidget;
}>();
</script>

<template>
  <div class="progress-card flex h-full flex-col justify-between p-4">
    <div class="text-muted-foreground text-sm">{{ widget.props.title }}</div>
    <div class="flex flex-1 items-center justify-center">
      <ElProgress
        type="dashboard"
        :percentage="widget.props.percentage"
        :status="widget.props.status || undefined"
        :stroke-width="widget.props.strokeWidth"
        :show-text="widget.props.showText"
      />
    </div>
  </div>
</template>

<style scoped>
/* 背景色由 WidgetRenderer 控制 */
</style>
