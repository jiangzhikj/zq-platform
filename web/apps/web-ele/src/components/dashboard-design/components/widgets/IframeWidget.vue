<script setup lang="ts">
import type { DashboardWidget } from '../../store/dashboardDesignStore';

import { computed, ref } from 'vue';

import { AlertCircle, ExternalLink, RefreshCw } from '@vben/icons';
import { $t } from '@vben/locales';

const props = defineProps<{
  isDesignMode?: boolean;
  widget: DashboardWidget;
}>();

const iframeRef = ref<HTMLIFrameElement | null>(null);
const isLoading = ref(true);
const hasError = ref(false);

const iframeUrl = computed(() => props.widget.props.url || '');

const handleLoad = () => {
  isLoading.value = false;
  hasError.value = false;
};

const handleError = () => {
  isLoading.value = false;
  hasError.value = true;
};

const refresh = () => {
  if (iframeRef.value) {
    isLoading.value = true;
    hasError.value = false;
    iframeRef.value.src = iframeUrl.value;
  }
};

const openInNewTab = () => {
  if (iframeUrl.value) {
    window.open(iframeUrl.value, '_blank');
  }
};
</script>

<template>
  <div class="iframe-widget flex h-full flex-col">
    <!-- 标题栏 -->
    <div v-if="widget.props.title" class="iframe-header">
      <span class="text-muted-foreground text-sm font-medium">{{
        widget.props.title
      }}</span>
      <div class="header-actions">
        <button class="action-btn" :title="$t('dashboard-design.widgets.iframe.refresh')" @click="refresh">
          <RefreshCw class="h-3.5 w-3.5" />
        </button>
        <button class="action-btn" :title="$t('dashboard-design.widgets.iframe.openNew')" @click="openInNewTab">
          <ExternalLink class="h-3.5 w-3.5" />
        </button>
      </div>
    </div>

    <!-- iframe 容器 -->
    <div class="iframe-container relative min-h-0 flex-1">
      <!-- 设计模式下显示占位 -->
      <div v-if="isDesignMode" class="design-placeholder">
        <ExternalLink class="h-8 w-8 text-gray-400" />
        <div class="mt-2 text-sm text-gray-500">{{ $t('dashboard-design.widgets.iframe.placeholder') }}</div>
        <div class="mt-1 max-w-full truncate px-4 text-xs text-gray-400">
          {{ iframeUrl || $t('dashboard-design.widgets.iframe.noUrl') }}
        </div>
      </div>

      <!-- 实际 iframe -->
      <template v-else>
        <!-- 加载状态 -->
        <div v-if="isLoading" class="loading-overlay">
          <div class="loading-spinner"></div>
          <div class="mt-2 text-sm text-gray-500">{{ $t('dashboard-design.widgets.iframe.loading') }}</div>
        </div>

        <!-- 错误状态 -->
        <div v-if="hasError && !isLoading" class="error-overlay">
          <AlertCircle class="h-8 w-8 text-red-400" />
          <div class="mt-2 text-sm text-gray-500">{{ $t('dashboard-design.widgets.iframe.loadFailed') }}</div>
          <button class="text-primary mt-2 text-xs" @click="refresh">
            {{ $t('dashboard-design.widgets.iframe.retry') }}
          </button>
        </div>

        <!-- iframe -->
        <iframe
          v-show="!hasError"
          ref="iframeRef"
          :src="iframeUrl"
          :class="{ 'with-border': widget.props.showBorder }"
          :allowfullscreen="widget.props.allowFullscreen"
          frameborder="0"
          class="iframe-content"
          @load="handleLoad"
          @error="handleError"
        ></iframe>
      </template>
    </div>
  </div>
</template>

<style scoped>
.iframe-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.header-actions {
  display: flex;
  gap: 4px;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  color: var(--el-text-color-secondary);
  cursor: pointer;
  background: transparent;
  border: none;
  border-radius: 4px;
  transition: all 0.2s;
}

.action-btn:hover {
  color: var(--el-text-color-primary);
  background: var(--el-fill-color-light);
}

.iframe-container {
  position: relative;
  overflow: hidden;
}

.design-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  background: var(--el-fill-color-lighter);
}

.loading-overlay,
.error-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: var(--el-bg-color);
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--el-border-color-lighter);
  border-top-color: var(--el-color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.iframe-content {
  width: 100%;
  height: 100%;
}

.iframe-content.with-border {
  border: 1px solid var(--el-border-color-lighter);
}
</style>
