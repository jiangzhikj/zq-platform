<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue';

import {
  Code,
  Copy,
  Download,
  Eye,
  LayoutDashboard,
  Redo2,
  Trash2,
  Undo2,
  Upload,
} from '@vben/icons';
import { $t } from '@vben/locales';

import {
  ElButton,
  ElButtonGroup,
  ElEmpty,
  ElScrollbar,
  ElTooltip,
} from 'element-plus';
import { GridItem, GridLayout } from 'grid-layout-plus';

import {
  useDashboardDesignStore,
  widgetMaterials,
} from '../store/dashboardDesignStore';
import WidgetRenderer from './WidgetRenderer.vue';

defineProps<{
  showSave?: boolean;
}>();

const emit = defineEmits<{
  (e: 'preview'): void;
  (e: 'viewCode'): void;
  (e: 'clear'): void;
  (e: 'import'): void;
  (e: 'export'): void;
  (e: 'save'): void;
}>();

const store = useDashboardDesignStore();

// 布局数据 - 直接从 store 获取，不使用 computed setter 避免循环
const layout = computed(() =>
  store.dashboardConfig.widgets.map((w) => ({
    i: w.i,
    x: w.x,
    y: w.y,
    w: w.w,
    h: w.h,
    minW: w.minW,
    minH: w.minH,
    maxW: w.maxW,
    maxH: w.maxH,
  })),
);

// 拖拽相关
const isDragOver = ref(false);

const handleDragOver = (e: DragEvent) => {
  e.preventDefault();
  isDragOver.value = true;
};

const handleDragLeave = () => {
  isDragOver.value = false;
};

const handleDrop = (e: DragEvent) => {
  e.preventDefault();
  isDragOver.value = false;

  // 从 dataTransfer 获取组件类型
  const widgetType = e.dataTransfer?.getData('widget-type');
  if (widgetType) {
    const material = widgetMaterials.find((m) => m.type === widgetType);
    if (material) {
      // 计算拖放位置对应的网格坐标
      const target = e.currentTarget as HTMLElement;
      const rect = target.getBoundingClientRect();
      const offsetX = e.clientX - rect.left;
      const offsetY = e.clientY - rect.top;

      // 计算列宽（考虑 margin）
      const margin = store.dashboardConfig.margin;
      const colWidth =
        (rect.width - margin[0] * (store.dashboardConfig.columns + 1)) /
        store.dashboardConfig.columns;
      const rowHeight = store.dashboardConfig.rowHeight;

      // 转换为网格坐标
      const x = Math.max(
        0,
        Math.min(
          Math.floor(offsetX / (colWidth + margin[0])),
          store.dashboardConfig.columns - material.defaultW,
        ),
      );
      const y = Math.max(0, Math.floor(offsetY / (rowHeight + margin[1])));

      store.addWidget(material, { x, y });
    }
  }
};

// 布局变化
const handleLayoutUpdated = (newLayout: any[]) => {
  store.updateLayout(newLayout);
};

// 选中 widget
const handleWidgetClick = (id: string, e: MouseEvent) => {
  e.stopPropagation();
  store.setActive(id);
};

// 取消选中
const handleCanvasClick = () => {
  store.setActive(null);
};

// 删除 widget
const handleDelete = (id: string, e: MouseEvent) => {
  e.stopPropagation();
  store.deleteWidget(id);
};

// 复制 widget
const handleCopy = (id: string, e: MouseEvent) => {
  e.stopPropagation();
  store.copyWidget(id);
};

// 获取 widget 配置
const getWidget = (i: string) => {
  return store.dashboardConfig.widgets.find((w) => w.i === i);
};

// 获取 widget 材料信息
const getWidgetMaterial = (type: string) => {
  return widgetMaterials.find((m) => m.type === type);
};

// 获取动画延迟（交错入场效果）
const getAnimationDelay = (i: string) => {
  const index = store.dashboardConfig.widgets.findIndex((w) => w.i === i);
  return index * 80; // 每个组件延迟 80ms
};

// 右键菜单
const contextMenuVisible = ref(false);
const contextMenuPosition = ref({ x: 0, y: 0 });
const contextMenuWidgetId = ref<null | string>(null);

const handleContextMenu = (id: string, e: MouseEvent) => {
  e.preventDefault();
  e.stopPropagation();
  store.setActive(id);
  contextMenuWidgetId.value = id;
  contextMenuPosition.value = { x: e.clientX, y: e.clientY };
  contextMenuVisible.value = true;
};

const closeContextMenu = () => {
  contextMenuVisible.value = false;
  contextMenuWidgetId.value = null;
};

// 右键菜单操作
const handleContextMenuAction = (action: string) => {
  if (!contextMenuWidgetId.value) return;

  switch (action) {
    case 'copy': {
      store.copyWidget(contextMenuWidgetId.value);
      break;
    }
    case 'delete': {
      store.deleteWidget(contextMenuWidgetId.value);
      break;
    }
  }
  closeContextMenu();
};

// 键盘快捷键
const handleKeyDown = (e: KeyboardEvent) => {
  // 如果焦点在输入框中，不处理快捷键
  if (
    e.target instanceof HTMLInputElement ||
    e.target instanceof HTMLTextAreaElement
  ) {
    return;
  }

  // Delete 删除选中组件
  if ((e.key === 'Delete' || e.key === 'Backspace') && store.activeId) {
    e.preventDefault();
    store.deleteWidget(store.activeId);
  }

  // Ctrl+Z 撤销
  if ((e.ctrlKey || e.metaKey) && e.key === 'z' && !e.shiftKey) {
    e.preventDefault();
    store.undo();
  }

  // Ctrl+Y 或 Ctrl+Shift+Z 重做
  if (
    (e.ctrlKey || e.metaKey) &&
    (e.key === 'y' || (e.key === 'z' && e.shiftKey))
  ) {
    e.preventDefault();
    store.redo();
  }

  // Ctrl+C 复制
  if ((e.ctrlKey || e.metaKey) && e.key === 'c' && store.activeId) {
    e.preventDefault();
    store.copyWidget(store.activeId);
  }

  // Escape 取消选中
  if (e.key === 'Escape') {
    store.setActive(null);
    closeContextMenu();
  }
};

// 点击其他地方关闭右键菜单
const handleDocumentClick = () => {
  closeContextMenu();
};

onMounted(() => {
  document.addEventListener('keydown', handleKeyDown);
  document.addEventListener('click', handleDocumentClick);
});

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyDown);
  document.removeEventListener('click', handleDocumentClick);
});
</script>

<template>
  <div class="design-canvas flex h-full w-full flex-col gap-3">
    <!-- Header -->
    <div class="canvas-header flex items-center justify-between">
      <div class="flex items-center gap-2">
        <LayoutDashboard class="h-4 w-4" />
        <span class="font-medium">{{ $t('dashboard-design.canvas.title') }}</span>
        <span class="text-muted-foreground text-xs">
          {{ $t('dashboard-design.widgetCount', { count: store.dashboardConfig.widgets.length }) }}
        </span>
      </div>

      <div class="flex items-center gap-1">
        <!-- 撤销/重做 -->
        <ElButtonGroup size="small">
          <ElTooltip :content="$t('dashboard-design.canvas.undo') || '撤销'" placement="bottom">
            <ElButton :disabled="!store.canUndo" @click="store.undo">
              <Undo2 class="h-3.5 w-3.5" />
            </ElButton>
          </ElTooltip>
          <ElTooltip :content="$t('dashboard-design.canvas.redo') || '重做'" placement="bottom">
            <ElButton :disabled="!store.canRedo" @click="store.redo">
              <Redo2 class="h-3.5 w-3.5" />
            </ElButton>
          </ElTooltip>
        </ElButtonGroup>

        <div class="bg-border mx-1 h-4 w-px"></div>

        <!-- 操作按钮 -->
        <ElTooltip :content="$t('dashboard-design.preview')" placement="bottom">
          <ElButton size="small" @click="emit('preview')">
            <Eye class="h-3.5 w-3.5" />
          </ElButton>
        </ElTooltip>

        <ElTooltip :content="$t('dashboard-design.jsonPreview')" placement="bottom">
          <ElButton size="small" @click="emit('viewCode')">
            <Code class="h-3.5 w-3.5" />
          </ElButton>
        </ElTooltip>

        <ElTooltip :content="$t('dashboard-design.clear')" placement="bottom">
          <ElButton size="small" @click="emit('clear')">
            <Trash2 class="h-3.5 w-3.5" />
          </ElButton>
        </ElTooltip>

        <div class="bg-border mx-1 h-4 w-px"></div>

        <!-- 导入导出 -->
        <ElTooltip :content="$t('dashboard-design.import')" placement="bottom">
          <ElButton size="small" @click="emit('import')">
            <Upload class="h-3.5 w-3.5" />
          </ElButton>
        </ElTooltip>

        <ElTooltip :content="$t('dashboard-design.export')" placement="bottom">
          <ElButton size="small" @click="emit('export')">
            <Download class="h-3.5 w-3.5" />
          </ElButton>
        </ElTooltip>
      </div>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-hidden">
      <ElScrollbar class="h-full">
        <div
          class="canvas-container relative h-full"
          :class="{ 'drag-over': isDragOver }"
          @dragover="handleDragOver"
          @dragleave="handleDragLeave"
          @drop="handleDrop"
          @click="handleCanvasClick"
        >
          <ElEmpty
            v-if="store.dashboardConfig.widgets.length === 0"
            :description="$t('dashboard-design.dragTip')"
            class="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2"
          />

          <GridLayout
            v-else
            :layout="layout"
            :col-num="store.dashboardConfig.columns"
            :row-height="store.dashboardConfig.rowHeight"
            :margin="store.dashboardConfig.margin"
            :is-draggable="true"
            :is-resizable="true"
            :vertical-compact="true"
            :use-css-transforms="true"
            @layout-updated="handleLayoutUpdated"
          >
            <GridItem
              v-for="item in layout"
              :key="item.i"
              :i="item.i"
              :x="item.x"
              :y="item.y"
              :w="item.w"
              :h="item.h"
              :min-w="item.minW"
              :min-h="item.minH"
              :max-w="item.maxW"
              :max-h="item.maxH"
              class="widget-item"
              :class="{ active: store.activeId === item.i }"
              @click="handleWidgetClick(item.i, $event)"
              @contextmenu="handleContextMenu(item.i, $event)"
            >
              <div class="widget-wrapper h-full w-full">
                <!-- 操作按钮 -->
                <div v-if="store.activeId === item.i" class="widget-actions">
                  <button
                    class="action-btn"
                    :title="$t('dashboard-design.copy')"
                    @click="handleCopy(item.i, $event)"
                  >
                    <Copy class="h-3.5 w-3.5" />
                  </button>
                  <button
                    class="action-btn delete"
                    :title="$t('dashboard-design.delete')"
                    @click="handleDelete(item.i, $event)"
                  >
                    <Trash2 class="h-3.5 w-3.5" />
                  </button>
                </div>

                <!-- Widget 内容 -->
                <WidgetRenderer
                  v-if="getWidget(item.i)"
                  :widget="getWidget(item.i)!"
                  :material="getWidgetMaterial(getWidget(item.i)!.type)"
                  :is-design-mode="true"
                  :animation-delay="getAnimationDelay(item.i)"
                />
              </div>
            </GridItem>
          </GridLayout>
        </div>
      </ElScrollbar>
    </div>

    <!-- 右键菜单 -->
    <Teleport to="body">
      <div
        v-if="contextMenuVisible"
        class="context-menu"
        :style="{
          left: `${contextMenuPosition.x}px`,
          top: `${contextMenuPosition.y}px`,
        }"
        @click.stop
      >
        <div class="context-menu-item" @click="handleContextMenuAction('copy')">
          <Copy class="h-4 w-4" />
          <span>{{ $t('dashboard-design.copy') }}</span>
          <span class="shortcut">Ctrl+C</span>
        </div>
        <div
          class="context-menu-item delete"
          @click="handleContextMenuAction('delete')"
        >
          <Trash2 class="h-4 w-4" />
          <span>{{ $t('dashboard-design.delete') }}</span>
          <span class="shortcut">Delete</span>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.design-canvas {
  overflow: hidden;
  background-color: var(--el-bg-color-page);
  border-radius: 8px;
}

.canvas-header {
  flex-shrink: 0;
  padding: 12px 16px;
  background-color: var(--el-bg-color);
  border-radius: 8px;
}

:deep(.el-scrollbar__wrap) {
  height: 100%;
}

:deep(.el-scrollbar__view) {
  height: 100%;
}

.canvas-container {
  background-color: var(--el-color-primary-light-9);
  background-image: radial-gradient(
    circle,
    var(--el-border-color-lighter) 1px,
    transparent 1px
  );
  background-size: 20px 20px;
  border-radius: 8px;
  transition: background-color 0.2s;
}

.canvas-container.drag-over {
  background-color: var(--el-color-primary-light-9);
}

.widget-item {
  overflow: hidden;
  background: var(--el-bg-color);
  border: 2px solid transparent;
  border-radius: 8px;
  transition:
    border-color 0.2s,
    box-shadow 0.2s;
}

.widget-item:hover {
  border-color: var(--el-color-primary-light-5);
}

.widget-item.active {
  border-color: var(--el-color-primary);
  box-shadow: 0 0 0 2px var(--el-color-primary-light-7);
}

.widget-wrapper {
  position: relative;
}

.widget-actions {
  position: absolute;
  top: -32px;
  right: 0;
  z-index: 10;
  display: flex;
  gap: 4px;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  color: var(--el-text-color-regular);
  cursor: pointer;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
  transition: all 0.2s;
}

.action-btn:hover {
  color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
  border-color: var(--el-color-primary);
}

.action-btn.delete:hover {
  color: var(--el-color-danger);
  background: var(--el-color-danger-light-9);
  border-color: var(--el-color-danger);
}

/* Grid Layout 样式覆盖 */
:deep(.vue-grid-item) {
  touch-action: none;
}

:deep(.vue-grid-item.vue-grid-placeholder) {
  background: var(--el-color-primary-light-7) !important;
  border: 2px dashed var(--el-color-primary) !important;
  border-radius: 8px;
}

:deep(.vue-resizable-handle) {
  right: 4px;
  bottom: 4px;
  width: 16px;
  height: 16px;
  background: none;
}

:deep(.vue-resizable-handle::after) {
  position: absolute;
  right: 4px;
  bottom: 4px;
  width: 8px;
  height: 8px;
  content: '';
  border-right: 2px solid var(--el-border-color);
  border-bottom: 2px solid var(--el-border-color);
}

.widget-item.active :deep(.vue-resizable-handle::after) {
  border-color: var(--el-color-primary);
}

/* 右键菜单样式 */
.context-menu {
  position: fixed;
  z-index: 9999;
  min-width: 160px;
  padding: 4px 0;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-light);
  border-radius: 6px;
  box-shadow: 0 4px 12px rgb(0 0 0 / 15%);
}

.context-menu-item {
  display: flex;
  gap: 8px;
  align-items: center;
  padding: 8px 12px;
  font-size: 13px;
  color: var(--el-text-color-regular);
  cursor: pointer;
  transition: all 0.15s;
}

.context-menu-item:hover {
  color: var(--el-color-primary);
  background: var(--el-fill-color-light);
}

.context-menu-item.delete:hover {
  color: var(--el-color-danger);
  background: var(--el-color-danger-light-9);
}

.context-menu-item .shortcut {
  margin-left: auto;
  font-size: 12px;
  color: var(--el-text-color-placeholder);
}

.context-menu-divider {
  height: 1px;
  margin: 4px 0;
  background: var(--el-border-color-lighter);
}
</style>
