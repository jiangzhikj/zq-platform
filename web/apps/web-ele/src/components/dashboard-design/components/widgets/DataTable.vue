<script setup lang="ts">
import { computed } from 'vue';

import { $t } from '@vben/locales';

import type { DashboardWidget } from '../../store/dashboardDesignStore';

import { ElTable, ElTableColumn } from 'element-plus';

const props = defineProps<{
  widget: DashboardWidget;
}>();

const columns = computed(() => props.widget.props.columns || []);
const tableData = computed(() => props.widget.props.data || []);

// 状态颜色映射
const getStatusClass = (status: string) => {
  const statusMap: Record<string, string> = {
    [$t('dashboard-design.widgets.dataTable.status.normal')]: 'status-success',
    [$t('dashboard-design.widgets.dataTable.status.warning')]: 'status-warning',
    [$t('dashboard-design.widgets.dataTable.status.error')]: 'status-danger',
    [$t('dashboard-design.widgets.dataTable.status.success')]: 'status-success',
    [$t('dashboard-design.widgets.dataTable.status.failed')]: 'status-danger',
    [$t('dashboard-design.widgets.dataTable.status.processing')]: 'status-info',
  };
  return statusMap[status] || '';
};
</script>

<template>
  <div class="data-table-widget flex h-full flex-col p-3">
    <div
      v-if="widget.props.title"
      class="text-muted-foreground mb-2 text-sm font-medium"
    >
      {{ widget.props.title }}
    </div>

    <div class="min-h-0 flex-1 overflow-hidden">
      <ElTable
        :data="tableData"
        :stripe="widget.props.stripe"
        :border="widget.props.border"
        :size="widget.props.size || 'default'"
        height="100%"
        class="h-full"
      >
        <ElTableColumn
          v-if="widget.props.showIndex"
          type="index"
          label="#"
          width="50"
        />
        <ElTableColumn
          v-for="col in columns"
          :key="col.prop"
          :prop="col.prop"
          :label="col.label"
          :width="col.width"
          :min-width="col.minWidth"
        >
          <template #default="{ row }">
            <span
              v-if="col.prop === 'status'"
              :class="getStatusClass(row[col.prop])"
            >
              {{ row[col.prop] }}
            </span>
            <span v-else>{{ row[col.prop] }}</span>
          </template>
        </ElTableColumn>
      </ElTable>
    </div>
  </div>
</template>

<style scoped>
.data-table-widget :deep(.el-table) {
  --el-table-header-bg-color: var(--el-fill-color-light);
}

.status-success {
  color: var(--el-color-success);
}

.status-warning {
  color: var(--el-color-warning);
}

.status-danger {
  color: var(--el-color-danger);
}

.status-info {
  color: var(--el-color-info);
}
</style>
