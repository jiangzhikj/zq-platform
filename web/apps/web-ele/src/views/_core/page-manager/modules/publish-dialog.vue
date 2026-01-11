<script lang="ts" setup>
import type { MenuItem } from '#/components/zq-form/zq-menu-selector/types';

import { computed, ref, watch } from 'vue';

import { $t } from '@vben/locales';

import {
  ElButton,
  ElDialog,
  ElForm,
  ElFormItem,
  ElInput,
  ElInputNumber,
  ElMessage,
} from 'element-plus';

import { publishPageApi } from '#/api/core/page-manager';
import { ZqMenuSelector } from '#/components/zq-form/zq-menu-selector';

interface Props {
  modelValue: boolean;
  pageId: string;
  pageName: string;
  pageCode: string;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  published: [];
  'update:modelValue': [value: boolean];
}>();

const dialogVisible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
});

const loading = ref(false);

// 发布表单
const publishForm = ref({
  menu_name: '',
  menu_parent_id: '',
  menu_icon: 'lucide:layout-dashboard',
  menu_order: 0,
});

// 监听弹窗打开
watch(
  () => props.modelValue,
  (visible) => {
    if (visible) {
      // 初始化表单
      publishForm.value.menu_name = props.pageName;
    }
  },
);

// 菜单选择回调
function handleMenuChange(menu: MenuItem | MenuItem[] | null) {
  if (Array.isArray(menu)) {
    publishForm.value.menu_parent_id = menu[0]?.id || '';
  } else {
    publishForm.value.menu_parent_id = menu?.id || '';
  }
}

async function handlePublish() {
  if (!publishForm.value.menu_name) {
    ElMessage.warning($t('page-manager.placeholder.name'));
    return;
  }

  loading.value = true;
  try {
    await publishPageApi(props.pageId, {
      menu_name: publishForm.value.menu_name,
      menu_parent_id: publishForm.value.menu_parent_id || undefined,
      menu_icon: publishForm.value.menu_icon,
      menu_order: publishForm.value.menu_order,
    });
    ElMessage.success($t('page-manager.publishDialog.success'));
    emit('published');
    dialogVisible.value = false;
  } catch (error: any) {
    ElMessage.error(error?.message || $t('page-manager.publishDialog.failed'));
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <ElDialog
    v-model="dialogVisible"
    :title="$t('page-manager.publishDialog.title')"
    width="500px"
    :close-on-click-modal="false"
  >
    <ElForm :model="publishForm" label-width="100px" label-position="right">
      <ElFormItem :label="$t('page-manager.publishDialog.menuName')" required>
        <ElInput
          v-model="publishForm.menu_name"
          :placeholder="$t('page-manager.placeholder.name')"
          clearable
        />
      </ElFormItem>
      <ElFormItem :label="$t('page-manager.publishDialog.parentMenu')">
        <ZqMenuSelector
          :model-value="publishForm.menu_parent_id || null"
          mode="dialog"
          :placeholder="$t('page-manager.publishDialog.parentMenuPlaceholder')"
          @change="handleMenuChange"
        />
      </ElFormItem>
      <ElFormItem :label="$t('page-manager.publishDialog.menuIcon')">
        <ElInput
          v-model="publishForm.menu_icon"
          :placeholder="$t('common.placeholder')"
          clearable
        />
      </ElFormItem>
      <ElFormItem :label="$t('common.sort')">
        <ElInputNumber
          v-model="publishForm.menu_order"
          :min="0"
          :max="9999"
          controls-position="right"
        />
      </ElFormItem>
    </ElForm>

    <template #footer>
      <ElButton @click="dialogVisible = false">{{ $t('common.cancel') }}</ElButton>
      <ElButton type="primary" :loading="loading" @click="handlePublish">
        {{ $t('page-manager.publish') }}
      </ElButton>
    </template>
  </ElDialog>
</template>
