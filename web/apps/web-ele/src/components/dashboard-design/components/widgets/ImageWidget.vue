<script setup lang="ts">
import type { DashboardWidget } from '../../store/dashboardDesignStore';

import { computed } from 'vue';

import { ElImage } from 'element-plus';

import { getFileStreamUrl } from '#/api/core/file';

const props = defineProps<{
  isDesignMode?: boolean;
  widget: DashboardWidget;
}>();

const widgetProps = computed(() => props.widget.props);

// 解析图片URL，支持 file:// 前缀的文件ID
const resolveImageUrl = (url: string): string => {
  if (!url) return '';
  if (url.startsWith('file://')) {
    const fileId = url.slice(7); // 移除 'file://' 前缀
    return getFileStreamUrl(fileId);
  }
  return url;
};

// 主图URL
const imageSrc = computed(() => resolveImageUrl(widgetProps.value.src || ''));

// 预览图片列表
const previewList = computed(() => {
  const list = widgetProps.value.previewSrcList || [];
  // 如果没有配置预览列表，则使用当前图片
  if (list.length === 0 && imageSrc.value) {
    return [imageSrc.value];
  }
  return list.map((url: string) => resolveImageUrl(url));
});
</script>

<template>
  <div class="image-widget flex h-full w-full flex-col">
    <!-- 标题 -->
    <div
      v-if="widgetProps.title"
      class="mb-2 flex-shrink-0 text-sm font-medium"
      style="color: var(--el-text-color-primary)"
    >
      {{ widgetProps.title }}
    </div>

    <!-- 图片容器 -->
    <div class="relative min-h-0 flex-1 overflow-hidden rounded">
      <ElImage
        :src="imageSrc"
        :alt="widgetProps.alt || '图片'"
        :fit="widgetProps.fit || 'cover'"
        :lazy="widgetProps.lazy !== false"
        :preview-src-list="isDesignMode ? [] : previewList"
        :z-index="widgetProps.zIndex || 2000"
        :hide-on-click-modal="widgetProps.hideOnClickModal || false"
        class="h-full w-full"
        :preview-teleported="true"
      >
        <template #error>
          <div
            class="flex h-full w-full items-center justify-center"
            style="background-color: var(--el-fill-color-light)"
          >
            <span style="color: var(--el-text-color-secondary)">
              加载失败
            </span>
          </div>
        </template>
        <template #placeholder>
          <div
            class="flex h-full w-full items-center justify-center"
            style="background-color: var(--el-fill-color-lighter)"
          >
            <span style="color: var(--el-text-color-placeholder)">
              加载中...
            </span>
          </div>
        </template>
      </ElImage>
    </div>
  </div>
</template>

<style scoped>
.image-widget :deep(.el-image) {
  display: block;
}

.image-widget :deep(.el-image__inner) {
  transition: transform 0.3s ease;
}

.image-widget:hover :deep(.el-image__inner) {
  transform: scale(1.02);
}
</style>
