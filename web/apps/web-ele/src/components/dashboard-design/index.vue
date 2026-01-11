<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue';

import { Code, RotateCw, Upload } from '@vben/icons';
import { $t } from '@vben/locales';

import {
  ElButton,
  ElDialog,
  ElInput,
  ElMessage,
  ElMessageBox,
} from 'element-plus';

import AttributePanel from './components/AttributePanel.vue';
import DesignCanvas from './components/DesignCanvas.vue';
import MaterialPanel from './components/MaterialPanel.vue';
import PreviewModal from './components/PreviewModal.vue';
import { useDashboardDesignStore } from './store/dashboardDesignStore';

const props = defineProps<{
  // 初始配置 JSON
  initialConfig?: string;
}>();

const emit = defineEmits<{
  (e: 'save', config: string): void;
}>();

const store = useDashboardDesignStore();

// 预览弹窗
const previewVisible = ref(false);

// 代码弹窗
const codeVisible = ref(false);
const codeContent = ref('');

// 导入弹窗
const importVisible = ref(false);
const importContent = ref('');

// 初始化配置
if (props.initialConfig) {
  store.importConfig(props.initialConfig);
}

// 预览
const handlePreview = () => {
  if (store.dashboardConfig.widgets.length === 0) {
    ElMessage.warning($t('dashboard-design.noWidgetsTip'));
    return;
  }
  previewVisible.value = true;
};

// 查看代码
const handleViewCode = () => {
  codeContent.value = store.exportConfig();
  codeVisible.value = true;
};

// 保存
const handleSave = () => {
  const config = store.exportConfig();
  emit('save', config);
  ElMessage.success($t('dashboard-design.saveSuccess'));
};

// 清空画布
const handleClear = async () => {
  if (store.dashboardConfig.widgets.length === 0) {
    return;
  }

  try {
    await ElMessageBox.confirm($t('dashboard-design.clearConfirm'), $t('common.tips'), {
      confirmButtonText: $t('common.confirm'),
      cancelButtonText: $t('common.cancel'),
      type: 'warning',
    });
    store.clearCanvas();
    ElMessage.success($t('dashboard-design.clearSuccess'));
  } catch {
    // 取消操作
  }
};

// 导出配置
const handleExport = () => {
  const config = store.exportConfig();
  const blob = new Blob([config], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `dashboard-${Date.now()}.json`;
  a.click();
  URL.revokeObjectURL(url);
  ElMessage.success($t('dashboard-design.exportSuccess'));
};

// 打开导入弹窗
const handleOpenImport = () => {
  importContent.value = '';
  importVisible.value = true;
};

// 确认导入
const handleImport = () => {
  if (!importContent.value.trim()) {
    ElMessage.warning($t('dashboard-design.importEmpty'));
    return;
  }

  const success = store.importConfig(importContent.value);
  if (success) {
    importVisible.value = false;
    ElMessage.success($t('dashboard-design.importSuccess'));
  } else {
    ElMessage.error($t('dashboard-design.importError'));
  }
};

// 复制代码
const handleCopyCode = async () => {
  try {
    await navigator.clipboard.writeText(codeContent.value);
    ElMessage.success($t('dashboard-design.copySuccess'));
  } catch {
    ElMessage.error($t('dashboard-design.copyError'));
  }
};

// 键盘快捷键处理
const handleKeyDown = (e: KeyboardEvent) => {
  // 如果正在输入框中，不处理快捷键
  const target = e.target as HTMLElement;
  if (
    target.tagName === 'INPUT' ||
    target.tagName === 'TEXTAREA' ||
    target.isContentEditable
  ) {
    return;
  }

  // 如果弹窗打开，不处理快捷键
  if (previewVisible.value || codeVisible.value || importVisible.value) {
    return;
  }

  const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
  const ctrlKey = isMac ? e.metaKey : e.ctrlKey;

  // Ctrl+Z 撤销
  if (ctrlKey && e.key === 'z' && !e.shiftKey) {
    e.preventDefault();
    if (store.canUndo) {
      store.undo();
      ElMessage.success($t('dashboard-design.undoSuccess'));
    }
    return;
  }

  // Ctrl+Y 或 Ctrl+Shift+Z 重做
  if ((ctrlKey && e.key === 'y') || (ctrlKey && e.shiftKey && e.key === 'z')) {
    e.preventDefault();
    if (store.canRedo) {
      store.redo();
      ElMessage.success($t('dashboard-design.redoSuccess'));
    }
    return;
  }

  // Ctrl+C 复制
  if (ctrlKey && e.key === 'c') {
    if (store.activeId) {
      e.preventDefault();
      store.copyToClipboard(store.activeId);
      ElMessage.success($t('dashboard-design.copyWidgetSuccess'));
    }
    return;
  }

  // Ctrl+V 粘贴
  if (ctrlKey && e.key === 'v') {
    if (store.hasClipboard) {
      e.preventDefault();
      store.pasteFromClipboard();
      ElMessage.success($t('dashboard-design.pasteWidgetSuccess'));
    }
    return;
  }

  // Delete 或 Backspace 删除
  if (e.key === 'Delete' || e.key === 'Backspace') {
    if (store.activeId) {
      e.preventDefault();
      store.deleteWidget(store.activeId);
      ElMessage.success($t('dashboard-design.deleteWidgetSuccess'));
    }
    return;
  }

  // Ctrl+S 保存
  if (ctrlKey && e.key === 's') {
    e.preventDefault();
    handleSave();
    
  }
};

// 注册/注销键盘事件
onMounted(() => {
  window.addEventListener('keydown', handleKeyDown);
});

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown);
});
</script>

<template>
  <div class="dashboard-design flex h-full w-full overflow-hidden">
    <!-- 主体区域 -->
    <div class="bg-background-deep flex flex-1 gap-3 overflow-hidden p-3">
      <!-- 左侧：组件面板 -->
      <div class="h-full flex-shrink-0">
        <MaterialPanel />
      </div>

      <!-- 中间：设计画布 -->
      <div class="relative h-full min-w-0 flex-1 overflow-hidden">
        <DesignCanvas
          @preview="handlePreview"
          @view-code="handleViewCode"
          @clear="handleClear"
          @import="handleOpenImport"
          @export="handleExport"
          @save="handleSave"
        />
      </div>

      <!-- 右侧：属性面板 -->
      <div class="h-full flex-shrink-0">
        <AttributePanel />
      </div>
    </div>

    <!-- 预览弹窗 -->
    <PreviewModal v-model:visible="previewVisible" />

    <!-- JSON预览弹窗 -->
    <ElDialog
      v-model="codeVisible"
      :title="$t('dashboard-design.jsonPreview')"
      width="800px"
      :close-on-click-modal="false"
    >
      <template #header>
        <div class="flex items-center gap-2">
          <Code class="h-5 w-5" />
          <span>{{ $t('dashboard-design.jsonPreview') }}</span>
        </div>
      </template>
      <div class="code-container">
        <pre
          class="bg-background-deep overflow-auto rounded-lg p-4 text-sm"
        ><code>{{ codeContent }}</code></pre>
      </div>
      <template #footer>
        <ElButton @click="handleCopyCode"> {{ $t('dashboard-design.copyCode') }} </ElButton>
        <ElButton type="primary" @click="codeVisible = false"> {{ $t('common.close') }} </ElButton>
      </template>
    </ElDialog>

    <!-- 导入弹窗 -->
    <ElDialog
      v-model="importVisible"
      :title="$t('dashboard-design.importTitle')"
      width="600px"
      :close-on-click-modal="false"
    >
      <template #header>
        <div class="flex items-center gap-2">
          <Upload class="h-5 w-5" />
          <span>{{ $t('dashboard-design.importTitle') }}</span>
        </div>
      </template>
      <ElInput
        v-model="importContent"
        type="textarea"
        :rows="15"
        :placeholder="$t('dashboard-design.importPlaceholder')"
      />
      <template #footer>
        <ElButton @click="importVisible = false">{{ $t('common.cancel') }}</ElButton>
        <ElButton type="primary" @click="handleImport">
          <RotateCw class="mr-1 h-4 w-4" />
          {{ $t('dashboard-design.import') }}
        </ElButton>
      </template>
    </ElDialog>
  </div>
</template>

<style scoped>
.dashboard-design {
  height: 100%;
}

.code-container {
  max-height: 500px;
  overflow: auto;
}

.code-container pre {
  margin: 0;
  word-break: break-all;
  white-space: pre-wrap;
}
</style>
