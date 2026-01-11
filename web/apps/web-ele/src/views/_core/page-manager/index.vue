<script lang="ts" setup>
import type { PageMetaListItem } from '#/api/core/page-manager';

import { ref } from 'vue';

import { Page } from '@vben/common-ui';
import {
  Copy,
  Edit,
  Eye,
  MoreHorizontal,
  Play,
  Plus,
  Square,
  Trash2,
} from '@vben/icons';
import { $t } from '@vben/locales';

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
  batchDeletePageApi,
  copyPageApi,
  deletePageApi,
  getPageListApi,
  unpublishPageApi,
} from '#/api/core/page-manager';
import { useZqTable } from '#/components/zq-table';

import PageEditorModal from './modules/page-editor-modal.vue';
import PreviewDialog from './modules/preview-dialog.vue';
import PublishDialog from './modules/publish-dialog.vue';

defineOptions({ name: 'PageManager' });

// 列表 API
const fetchPageList = async (params: any) => {
  const res = await getPageListApi({
    page: params.page.currentPage,
    pageSize: params.page.pageSize,
    name: params.form?.name,
    code: params.form?.code,
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
      { key: 'name', title: $t('page-manager.name'), minWidth: 150 },
      { key: 'code', title: $t('page-manager.code'), minWidth: 120 },
      {
        key: 'status',
        title: $t('page-manager.status'),
        width: 100,
        align: 'center',
      },
      { key: 'description', title: $t('page-manager.description'), minWidth: 200 },
      { key: 'sys_create_datetime', title: $t('page-manager.createTime'), width: 170 },
      { key: 'sys_update_datetime', title: $t('page-manager.updateTime'), width: 170 },
      {
        key: 'actions',
        title: $t('page-manager.actions'),
        width: 220,
        fixed: 'right' as any,
        align: 'center',
        slots: { default: 'cell-actions' },
      },
    ],
    border: true,
    stripe: true,
    showSelection: true,
    showIndex: true,
    proxyConfig: {
      autoLoad: true,
      ajax: {
        query: fetchPageList,
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
        label: $t('page-manager.name'),
        component: 'Input',
        componentProps: {
          placeholder: $t('page-manager.placeholder.name'),
        },
      },
      {
        fieldName: 'code',
        label: $t('page-manager.code'),
        component: 'Input',
        componentProps: {
          placeholder: $t('page-manager.placeholder.code'),
        },
      },
      {
        fieldName: 'status',
        label: $t('page-manager.status'),
        component: 'Select',
        componentProps: {
          options: [
            { label: $t('page-manager.statusMap.all'), value: '' },
            { label: $t('page-manager.statusMap.published'), value: 'published' },
            { label: $t('page-manager.statusMap.draft'), value: 'draft' },
          ],
        },
      },
    ],
    showCollapseButton: false,
    submitOnChange: false,
  },
});

const selectedItems = ref<PageMetaListItem[]>([]);
const showPageEditor = ref(false);
const editingPageId = ref<null | string>(null);

// 发布弹窗状态
const showPublishDialog = ref(false);
const publishingPage = ref<null | PageMetaListItem>(null);

// 预览弹窗状态
const showPreviewDialog = ref(false);
const previewingPageId = ref<null | string>(null);

function handleSelectionChange(items: Record<string, any>[]) {
  selectedItems.value = items as PageMetaListItem[];
}

function handleCreate() {
  editingPageId.value = null;
  showPageEditor.value = true;
}

function handleEdit(item: PageMetaListItem) {
  editingPageId.value = item.id;
  showPageEditor.value = true;
}

function handlePreview(item: PageMetaListItem) {
  previewingPageId.value = item.id;
  showPreviewDialog.value = true;
}

async function handleDelete(item: PageMetaListItem) {
  try {
    await ElMessageBox.confirm(
      $t('page-manager.deleteConfirm', { name: item.name }),
      $t('page-manager.deleteConfirmTitle'),
      {
        confirmButtonText: $t('common.confirm'),
        cancelButtonText: $t('common.cancel'),
        type: 'warning',
      },
    );
    await deletePageApi(item.id);
    ElMessage.success($t('page-manager.deleteSuccess', { name: item.name }));
    gridApi.reload();
  } catch {
    // 用户取消或删除失败
  }
}

async function handleBatchDelete() {
  if (selectedItems.value.length === 0) return;

  try {
    await ElMessageBox.confirm(
      $t('page-manager.batchDeleteConfirm', { count: selectedItems.value.length }),
      $t('page-manager.batchDeleteConfirmTitle'),
      {
        confirmButtonText: $t('common.confirm'),
        cancelButtonText: $t('common.cancel'),
        type: 'warning',
      },
    );
    const ids = selectedItems.value.map((item) => item.id);
    await batchDeletePageApi(ids);
    ElMessage.success($t('page-manager.batchDeleteSuccess', { count: selectedItems.value.length }));
    selectedItems.value = [];
    gridApi.reload();
  } catch {
    // 用户取消或删除失败
  }
}

function handlePublish(item: PageMetaListItem) {
  publishingPage.value = item;
  showPublishDialog.value = true;
}

function handlePublished() {
  gridApi.reload();
}

async function handleUnpublish(item: PageMetaListItem) {
  try {
    await unpublishPageApi(item.id);
    ElMessage.success($t('page-manager.unpublishSuccess', { name: item.name }));
    gridApi.reload();
  } catch {
    ElMessage.error($t('page-manager.unpublishFailed'));
  }
}

async function handleCopy(item: PageMetaListItem) {
  try {
    const { value: newCode } = await ElMessageBox.prompt(
      $t('page-manager.copyCodePlaceholder'),
      $t('page-manager.copyTitle'),
      {
        confirmButtonText: $t('common.confirm'),
        cancelButtonText: $t('common.cancel'),
        inputPattern: /^[\w-]+$/,
        inputErrorMessage: $t('page-manager.copyCodeRule'),
        inputValue: `${item.code}_copy`,
      },
    );
    await copyPageApi(item.id, newCode, `${item.name} (${$t('page-manager.copy')})`);
    ElMessage.success($t('page-manager.copySuccess'));
    gridApi.reload();
  } catch {
    // 用户取消
  }
}

function handlePageSave() {
  ElMessage.success($t('page-manager.saveSuccess'));
  gridApi.reload();
}

// 处理更多菜单命令
function handleCommand(command: string, row: PageMetaListItem) {
  switch (command) {
    case 'copy': {
      handleCopy(row);
      break;
    }
    case 'preview': {
      handlePreview(row);
      break;
    }
    case 'publish': {
      handlePublish(row);
      break;
    }
    case 'unpublish': {
      handleUnpublish(row);
      break;
    }
  }
}
</script>

<template>
  <Page auto-content-height>
    <Grid @selection-change="handleSelectionChange">
      <!-- 工具栏操作 -->
      <template #toolbar-actions>
        <ElButton type="primary" :icon="Plus" @click="handleCreate">
          {{ $t('page-manager.create') }}
        </ElButton>
        <ElButton
          type="danger"
          :icon="Trash2"
          :disabled="selectedItems.length === 0"
          @click="handleBatchDelete"
        >
          {{
            selectedItems.length > 0
              ? $t('page-manager.batchDeleteWithCount', { count: selectedItems.length })
              : $t('page-manager.batchDelete')
          }}
        </ElButton>
      </template>

      <!-- 状态列 -->
      <template #cell-status="{ row }">
        <ElTag
          :type="row.status === 'published' ? 'success' : 'info'"
          size="small"
        >
          {{ row.status === 'published' ? $t('page-manager.statusMap.published') : $t('page-manager.statusMap.draft') }}
        </ElTag>
      </template>

      <!-- 操作列 -->
      <template #cell-actions="{ row }">
        <ElButton link type="primary" :icon="Edit" @click="handleEdit(row)">
          {{ $t('common.edit') }}
        </ElButton>
        <ElButton link type="danger" :icon="Trash2" @click="handleDelete(row)">
          {{ $t('common.delete') }}
        </ElButton>
        <ElDropdown
          trigger="click"
          @command="(cmd: string) => handleCommand(cmd, row)"
        >
          <ElButton link type="primary" :icon="MoreHorizontal"> {{ $t('page-manager.more') }} </ElButton>
          <template #dropdown>
            <ElDropdownMenu>
              <ElDropdownItem command="preview" :icon="Eye">
                {{ $t('page-manager.preview') }}
              </ElDropdownItem>
              <ElDropdownItem
                v-if="row.status === 'draft'"
                command="publish"
                :icon="Play"
              >
                {{ $t('page-manager.publish') }}
              </ElDropdownItem>
              <ElDropdownItem v-else command="unpublish" :icon="Square">
                {{ $t('page-manager.unpublish') }}
              </ElDropdownItem>
              <ElDropdownItem command="copy" :icon="Copy">
                {{ $t('page-manager.copy') }}
              </ElDropdownItem>
            </ElDropdownMenu>
          </template>
        </ElDropdown>
      </template>
    </Grid>

    <!-- 页面编辑器弹窗 -->
    <PageEditorModal
      v-model="showPageEditor"
      :page-id="editingPageId"
      @save="handlePageSave"
    />

    <!-- 预览弹窗 -->
    <PreviewDialog v-model="showPreviewDialog" :page-id="previewingPageId" />

    <!-- 发布配置弹窗 -->
    <PublishDialog
      v-if="publishingPage"
      v-model="showPublishDialog"
      :page-id="publishingPage.id"
      :page-name="publishingPage.name"
      :page-code="publishingPage.code"
      @published="handlePublished"
    />
  </Page>
</template>
