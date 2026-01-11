<script lang="ts" setup>
import { computed, ref, watch } from 'vue';

import { $t } from '@vben/locales';

import { ElDialog, ElEmpty, ElMessage } from 'element-plus';

import { getPageDetailApi } from '#/api/core/page-manager';
import DashboardRenderer from '#/components/dashboard-design/DashboardRenderer.vue';

interface Props {
  modelValue: boolean;
  pageId?: null | string;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  'update:modelValue': [value: boolean];
}>();

const dialogVisible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
});

const loading = ref(false);
const pageConfig = ref<string>('');
const pageName = ref('');

// 监听弹窗打开
watch(
  () => props.modelValue,
  async (visible) => {
    if (visible && props.pageId) {
      await loadPageData(props.pageId);
    } else {
      pageConfig.value = '';
      pageName.value = '';
    }
  },
);

async function loadPageData(pageId: string) {
  loading.value = true;
  try {
    const page = await getPageDetailApi(pageId);
    pageName.value = page.name;
    pageConfig.value =
      page.page_config && Object.keys(page.page_config).length > 0
        ? JSON.stringify(page.page_config)
        : '';
  } catch (error: any) {
    ElMessage.error(error?.message || $t('page-manager.editor.loadFailed'));
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <ElDialog
    v-model="dialogVisible"
    :title="`${$t('page-manager.preview')} - ${pageName}`"
    width="90%"
    top="5vh"
    :close-on-click-modal="false"
    destroy-on-close
  >
    <div class="preview-container" style="height: 75vh">
      <DashboardRenderer v-if="pageConfig" :config="pageConfig" />
      <ElEmpty v-else :description="$t('page-manager.previewDialog.noConfig')" />
    </div>
  </ElDialog>
</template>

<style scoped>
.preview-container {
  overflow: hidden;
  background-color: var(--el-bg-color-page);
  border-radius: 8px;
}
</style>
