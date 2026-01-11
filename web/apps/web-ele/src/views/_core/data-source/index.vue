<script lang="ts" setup>
import type { DataSource } from '#/api/core/data-source';

import { ref } from 'vue';

import { $t } from '@vben/locales';
import { Page } from '@vben/common-ui';
import { Copy, Edit, MoreHorizontal, Play, Plus, Trash2 } from '@vben/icons';

import {
  ElButton,
  ElDropdown,
  ElDropdownItem,
  ElDropdownMenu,
  ElMessage,
  ElMessageBox,
  ElTag,
} from 'element-plus';

import {
  copyDataSourceApi,
  deleteDataSourceApi,
  getDataSourceListApi,
} from '#/api/core/data-source';
import { useZqTable } from '#/components/zq-table';

import DataSourceEditorModal from './modules/data-source-editor-modal.vue';
import TestDialog from './modules/test-dialog.vue';

defineOptions({ name: 'DataSourceManagement' });

// 列表 API
const fetchDataSourceList = async (params: any) => {
  const res = await getDataSourceListApi({
    page: params.page.currentPage,
    pageSize: params.page.pageSize,
    name: params.form?.name,
    code: params.form?.code,
    source_type: params.form?.source_type,
    status: params.form?.status,
  });
  return {
    items: res.items,
    total: res.total,
  };
};

// 使用 ZqTable
const [Grid, gridApi] = useZqTable({
  gridOptions: {
    columns: [
      { key: 'name', title: $t('data-source.dataSourceName'), minWidth: 150 },
      { key: 'code', title: $t('data-source.code'), minWidth: 120 },
      {
        key: 'source_type',
        title: $t('data-source.type'),
        width: 100,
        align: 'center',
      },
      {
        key: 'status',
        title: $t('data-source.status'),
        width: 80,
        align: 'center',
      },
      { key: 'description', title: $t('data-source.dataSourceDescription'), minWidth: 200 },
      { key: 'sys_create_datetime', title: $t('data-source.createTime'), width: 170 },
      {
        key: 'actions',
        title: $t('data-source.action'),
        width: 200,
        fixed: true,
        align: 'center',
      },
    ],
    border: true,
    stripe: true,
    showSelection: true,
    showIndex: true,
    proxyConfig: {
      autoLoad: true,
      ajax: {
        query: fetchDataSourceList,
      },
    },
    pagerConfig: {
      enabled: true,
      pageSize: 20,
    },
    toolbarConfig: {
      search: true,
      refresh: true,
      zoom: true,
      custom: true,
    },
  },
  formOptions: {
    schema: [
      {
        fieldName: 'name',
        label: $t('data-source.name'),
        component: 'Input',
        componentProps: {
          placeholder: $t('data-source.inputDataSourceName'),
        },
      },
      {
        fieldName: 'code',
        label: $t('data-source.code'),
        component: 'Input',
        componentProps: {
          placeholder: $t('data-source.inputCode'),
        },
      },
      {
        fieldName: 'source_type',
        label: $t('data-source.type'),
        component: 'Select',
        componentProps: {
          options: [
            { label: $t('data-source.all'), value: '' },
            { label: 'SQL', value: 'sql' },
            { label: 'API', value: 'api' },
            { label: $t('data-source.staticData'), value: 'static' },
          ],
        },
      },
      {
        fieldName: 'status',
        label: $t('data-source.status'),
        component: 'Select',
        componentProps: {
          options: [
            { label: $t('data-source.all'), value: '' },
            { label: $t('data-source.enable'), value: true },
            { label: $t('data-source.disable'), value: false },
          ],
        },
      },
    ],
    showCollapseButton: false,
    submitOnChange: false,
  },
});

const selectedItems = ref<DataSource[]>([]);
const showFormModal = ref(false);
const editingId = ref<null | string>(null);

// 测试弹窗状态
const showTestDialog = ref(false);
const testingDataSource = ref<DataSource | null>(null);

function handleSelectionChange(items: Record<string, any>[]) {
  selectedItems.value = items as DataSource[];
}

function handleCreate() {
  editingId.value = null;
  showFormModal.value = true;
}

function handleEdit(item: DataSource) {
  editingId.value = item.id;
  showFormModal.value = true;
}

function handleTest(item: DataSource) {
  testingDataSource.value = item;
  showTestDialog.value = true;
}

async function handleDelete(item: DataSource) {
  try {
    await ElMessageBox.confirm(
      $t('data-source.deleteConfirmMessage', { name: item.name }),
      $t('data-source.deleteConfirmTitle'),
      {
        confirmButtonText: $t('data-source.confirm'),
        cancelButtonText: $t('data-source.cancel'),
        type: 'warning',
      },
    );
    await deleteDataSourceApi(item.id);
    ElMessage.success($t('data-source.deleteSuccess', { name: item.name }));
    gridApi.reload();
  } catch {
    // 用户取消或删除失败
  }
}

async function handleBatchDelete() {
  if (selectedItems.value.length === 0) return;

  try {
    await ElMessageBox.confirm(
      $t('data-source.batchDeleteConfirmMessage', { count: selectedItems.value.length }),
      $t('data-source.batchDeleteConfirmTitle'),
      {
        confirmButtonText: $t('data-source.confirm'),
        cancelButtonText: $t('data-source.cancel'),
        type: 'warning',
      },
    );
    // 逐个删除
    for (const item of selectedItems.value) {
      await deleteDataSourceApi(item.id);
    }
    ElMessage.success($t('data-source.batchDeleteSuccess', { count: selectedItems.value.length }));
    selectedItems.value = [];
    gridApi.reload();
  } catch {
    // 用户取消或删除失败
  }
}

async function handleCopy(item: DataSource) {
  try {
    const { value: newCode } = await ElMessageBox.prompt(
      $t('data-source.inputNewCode'),
      $t('data-source.copyDataSource'),
      {
        confirmButtonText: $t('data-source.confirm'),
        cancelButtonText: $t('data-source.cancel'),
        inputPattern: /^[\w-]+$/,
        inputErrorMessage: $t('data-source.codeFormatError'),
        inputValue: `${item.code}_copy`,
      },
    );
    await copyDataSourceApi(item.id, {
      new_code: newCode,
      new_name: `${item.name} ${$t('data-source.copy')}`,
    });
    ElMessage.success($t('data-source.copySuccess'));
    gridApi.reload();
  } catch {
    // 用户取消
  }
}

function handleFormSave() {
  ElMessage.success($t('data-source.saveSuccess'));
  gridApi.reload();
}

// 处理更多菜单命令
function handleCommand(command: string, row: DataSource) {
  switch (command) {
    case 'copy': {
      handleCopy(row);
      break;
    }
    case 'test': {
      handleTest(row);
      break;
    }
  }
}

// 获取类型标签
function getTypeTag(type: string) {
  const map: Record<
    string,
    { label: string; type: 'primary' | 'success' | 'warning' }
  > = {
    sql: { label: 'SQL', type: 'primary' },
    api: { label: 'API', type: 'success' },
    static: { label: $t('data-source.staticLabel'), type: 'warning' },
  };
  return map[type] || { label: type, type: 'primary' };
}
</script>

<template>
  <Page auto-content-height>
    <Grid @selection-change="handleSelectionChange">
      <!-- 工具栏操作 -->
      <template #toolbar-actions>
        <ElButton type="primary" :icon="Plus" @click="handleCreate">
          {{ $t('data-source.createDataSource') }}
        </ElButton>
        <ElButton
          type="danger"
          plain
          :icon="Trash2"
          :disabled="selectedItems.length === 0"
          @click="handleBatchDelete"
        >
          {{
            selectedItems.length > 0
              ? `${$t('data-source.batchDelete')} (${selectedItems.length})`
              : $t('data-source.batchDelete')
          }}
        </ElButton>
      </template>

      <!-- 类型列 -->
      <template #cell-source_type="{ row }">
        <ElTag :type="getTypeTag(row.source_type).type" size="small">
          {{ getTypeTag(row.source_type).label }}
        </ElTag>
      </template>

      <!-- 状态列 -->
      <template #cell-status="{ row }">
        <ElTag :type="row.status ? 'success' : 'info'" size="small">
          {{ row.status ? $t('data-source.enable') : $t('data-source.disable') }}
        </ElTag>
      </template>

      <!-- 操作列 -->
      <template #cell-actions="{ row }">
        <ElButton link type="primary" :icon="Edit" @click="handleEdit(row)">
          {{ $t('data-source.edit') }}
        </ElButton>
        <ElButton link type="danger" :icon="Trash2" @click="handleDelete(row)">
          {{ $t('data-source.delete') }}
        </ElButton>
        <ElDropdown
          trigger="click"
          @command="(cmd: string) => handleCommand(cmd, row)"
        >
          <ElButton link type="primary" :icon="MoreHorizontal"> {{ $t('data-source.more') }} </ElButton>
          <template #dropdown>
            <ElDropdownMenu>
              <ElDropdownItem command="test" :icon="Play">
                {{ $t('data-source.testConnection') }}
              </ElDropdownItem>
              <ElDropdownItem command="copy" :icon="Copy">
                {{ $t('data-source.copy') }}
              </ElDropdownItem>
            </ElDropdownMenu>
          </template>
        </ElDropdown>
      </template>
    </Grid>

    <!-- 数据源编辑器弹窗 -->
    <DataSourceEditorModal
      v-model="showFormModal"
      :data-source-id="editingId"
      @save="handleFormSave"
    />

    <!-- 测试弹窗 -->
    <TestDialog
      v-if="testingDataSource"
      v-model="showTestDialog"
      :data-source="testingDataSource"
    />
  </Page>
</template>
