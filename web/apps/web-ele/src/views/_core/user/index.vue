<script lang="ts" setup>
import type {
  OnActionClickParams,
  VxeTableGridOptions,
} from '#/adapter/vxe-table';
import type { User } from '#/api/core';

import { ref } from 'vue';

import { Page, useVbenDrawer } from '@vben/common-ui';
import { Plus } from '@vben/icons';
import { $t } from '@vben/locales';

import { ElButton, ElMessage, ElMessageBox } from 'element-plus';

import { useVbenVxeGrid } from '#/adapter/vxe-table';
import {
  batchDeleteUserApi,
  deleteUserApi,
  getUserListApi,
  resetUserPasswordApi,
} from '#/api/core';
import { UserAvatar } from '#/components/user-avatar';

import { useColumns, useSearchFormSchema } from './data';
import Form from './modules/form.vue';

defineOptions({ name: 'SystemUser' });

const [FormDrawer, formDrawerApi] = useVbenDrawer({
  connectedComponent: Form,
  destroyOnClose: true,
});

const selectedRows = ref<User[]>([]);

/**
 * 编辑用户
 */
function onEdit(row: User) {
  formDrawerApi.setData(row).open();
}

/**
 * 创建新用户
 */
function onCreate() {
  formDrawerApi.setData({}).open();
}

/**
 * 删除单个用户
 */
function onDelete(row: User) {
  if (row.id === 'a0000000-0000-0000-0000-000000000001') {
    ElMessage.warning($t('user.cannotDeleteAdmin'));
    return;
  }

  ElMessageBox.confirm(
    $t('ui.actionMessage.deleteConfirm', [row.name]),
    $t('common.delete'),
    {
      confirmButtonText: $t('common.confirm'),
      cancelButtonText: $t('common.cancel'),
      type: 'warning',
    },
  )
    .then(async () => {
      try {
        await deleteUserApi(row.id);
        ElMessage.success($t('ui.actionMessage.deleteSuccess', [row.name]));
        refreshGrid();
      } catch {
        ElMessage.error($t('ui.actionMessage.deleteError'));
      }
    })
    .catch(() => {
      // 用户取消了操作
    });
}

/**
 * 批量删除用户
 */
function onBatchDelete() {
  if (selectedRows.value.length === 0) {
    ElMessage.warning($t('user.selectUsersToDelete'));
    return;
  }

  // 检查是否包含管理员账户
  const hasAdmin = selectedRows.value.some(
    (row) => row.id === 'a0000000-0000-0000-0000-000000000001',
  );
  if (hasAdmin) {
    ElMessage.warning($t('user.cannotDeleteAdmin'));
    return;
  }

  // 确认删除
  const names = selectedRows.value.map((row: User) => row.name).join('、');
  const confirmMessage = $t('user.batchDeleteConfirm', [
    selectedRows.value.length,
    names,
  ]);

  ElMessageBox.confirm(confirmMessage, $t('user.batchDeleteTitle'), {
    confirmButtonText: $t('common.confirm'),
    cancelButtonText: $t('common.cancel'),
    type: 'warning',
  })
    .then(async () => {
      try {
        const ids = selectedRows.value.map((row: User) => row.id);
        await batchDeleteUserApi({ ids });
        ElMessage.success(
          $t('user.deleteSuccess', [selectedRows.value.length]),
        );
        selectedRows.value = [];
        refreshGrid();
      } catch {
        ElMessage.error($t('user.deleteError'));
      }
    })
    .catch(() => {
      // 用户取消了操作
    });
}

/**
 * 重置密码
 */
function onResetPassword(row: User) {
  if (row.id === 'a0000000-0000-0000-0000-000000000001') {
    ElMessage.warning($t('user.cannotResetAdminPassword'));
    return;
  }

  ElMessageBox.confirm(
    $t('user.resetPasswordConfirm', [row.name]),
    $t('user.resetPasswordTitle'),
    {
      confirmButtonText: $t('common.confirm'),
      cancelButtonText: $t('common.cancel'),
      type: 'warning',
    },
  )
    .then(async () => {
      try {
        await resetUserPasswordApi(row.id);
        ElMessage.success($t('user.resetPasswordSuccess', [row.name]));
      } catch {
        ElMessage.error($t('user.resetPasswordError'));
      }
    })
    .catch(() => {
      // 用户取消了操作
    });
}

/**
 * 表格操作按钮的回调函数
 */
function onActionClick({ code, row }: OnActionClickParams<User>) {
  switch (code) {
    case 'delete': {
      onDelete(row);
      break;
    }
    case 'edit': {
      onEdit(row);
      break;
    }
    case 'reset-password': {
      onResetPassword(row);
      break;
    }
  }
}

const [Grid, gridApi] = useVbenVxeGrid({
  formOptions: {
    schema: useSearchFormSchema(),
    submitOnChange: true,
  },
  gridEvents: {
    checkboxAll: ({ records }: { records: User[] }) => {
      // 过滤掉管理员账户
      selectedRows.value = records.filter(
        (row) => row.id !== 'a0000000-0000-0000-0000-000000000001',
      );
    },
    checkboxChange: ({ records }: { records: User[] }) => {
      // 过滤掉管理员账户
      selectedRows.value = records.filter(
        (row) => row.id !== 'a0000000-0000-0000-0000-000000000001',
      );
    },
  },
  gridOptions: {
    columns: useColumns(onActionClick),
    height: 'auto',
    keepSource: true,
    proxyConfig: {
      ajax: {
        query: async ({ page }, formValues) => {
          const params = {
            page: page.currentPage,
            pageSize: page.pageSize,
            ...formValues,
          };
          return await getUserListApi(params);
        },
      },
    },
    checkboxConfig: {
      reserve: true,
      trigger: 'default',
      checkMethod: ({ row }: { row: User }) => {
        // 管理员账户不允许选择
        return row.id !== 'a0000000-0000-0000-0000-000000000001';
      },
    },
    toolbarConfig: {
      custom: true,
      export: false,
      refresh: { code: 'query' },
      search: true,
      zoom: true,
    },
  } as VxeTableGridOptions<User>,
});

/**
 * 刷新表格
 */
function refreshGrid() {
  gridApi.query();
}
</script>

<template>
  <Page auto-content-height>
    <FormDrawer @success="refreshGrid" />

    <Grid>
      <template #table-title>
        <ElButton type="primary" @click="onCreate">
          <Plus class="size-5" />
          {{ $t('ui.actionTitle.create', [$t('user.name')]) }}
        </ElButton>
        <ElButton type="danger" plain @click="onBatchDelete">
          {{ $t('user.batchDelete') }}
          {{ selectedRows.length > 0 ? `(${selectedRows.length})` : '' }}
        </ElButton>
      </template>

      <template #avatar="{ row }">
        <div class="flex items-center justify-center">
          <UserAvatar
            :user="row as any"
            :size="34"
            :font-size="16"
            :shadow="false"
          />
        </div>
      </template>
    </Grid>
  </Page>
</template>
