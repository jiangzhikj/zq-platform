<script setup lang="ts">
import { computed } from 'vue';

import { Maximize2, X } from '@vben/icons';
import { $t } from '@vben/locales';

import { ElButton, ElDialog, ElScrollbar } from 'element-plus';
import { GridItem, GridLayout } from 'grid-layout-plus';

import { useDashboardDesignStore } from '../store/dashboardDesignStore';
import WidgetRenderer from './WidgetRenderer.vue';

const props = defineProps<{
  visible: boolean;
}>();

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void;
}>();

const store = useDashboardDesignStore();

const dialogVisible = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val),
});

// 布局数据（只读）
const layout = computed(() =>
  store.dashboardConfig.widgets.map((w) => ({
    i: w.i,
    x: w.x,
    y: w.y,
    w: w.w,
    h: w.h,
  })),
);

// 获取 widget 配置
const getWidget = (i: string) => {
  return store.dashboardConfig.widgets.find((w) => w.i === i);
};

// 获取动画延迟（交错入场效果）
const getAnimationDelay = (i: string) => {
  const index = store.dashboardConfig.widgets.findIndex((w) => w.i === i);
  return index * 80; // 每个组件延迟 80ms
};

const handleClose = () => {
  dialogVisible.value = false;
};
</script>

<template>
  <ElDialog
    v-model="dialogVisible"
    :title="$t('dashboard-design.preview')"
    width="90%"
    top="5vh"
    :close-on-click-modal="false"
    destroy-on-close
    class="preview-dialog"
  >
    <template #header>
      <div class="flex items-center gap-2">
        <Maximize2 class="h-5 w-5" />
        <span class="text-lg font-medium">{{ $t('dashboard-design.title') }} - {{ $t('dashboard-design.preview') }}</span>
        <span class="text-muted-foreground ml-2 text-sm">
          {{ store.dashboardConfig.name }}
        </span>
      </div>
    </template>

    <ElScrollbar class="preview-content" style="height: 75vh">
      <div
        class="preview-container p-4"
        :style="{
          backgroundColor: store.dashboardConfig.backgroundColor || '',
        }"
      >
        <GridLayout
          v-if="layout.length > 0"
          :layout="layout"
          :col-num="store.dashboardConfig.columns"
          :row-height="store.dashboardConfig.rowHeight"
          :margin="store.dashboardConfig.margin"
          :is-draggable="false"
          :is-resizable="false"
          :vertical-compact="true"
          :use-css-transforms="true"
          :style="
            store.dashboardConfig.showOuterMargin
              ? {}
              : {
                  marginLeft: `-${store.dashboardConfig.margin[0]}px`,
                  marginRight: `-${store.dashboardConfig.margin[0]}px`,
                  marginTop: `-${store.dashboardConfig.margin[1]}px`,
                  width: `calc(100% + ${store.dashboardConfig.margin[0] * 2}px)`,
                }
          "
        >
          <GridItem
            v-for="item in layout"
            :key="item.i"
            :i="item.i"
            :x="item.x"
            :y="item.y"
            :w="item.w"
            :h="item.h"
            class="preview-widget"
          >
            <WidgetRenderer
              v-if="getWidget(item.i)"
              :widget="getWidget(item.i)!"
              :is-design-mode="false"
              :animation-delay="getAnimationDelay(item.i)"
            />
          </GridItem>
        </GridLayout>

        <div v-else class="flex h-64 items-center justify-center text-gray-400">
          {{ $t('dashboard-design.noWidgetsTip') }}
        </div>
      </div>
    </ElScrollbar>

    <template #footer>
      <ElButton @click="handleClose">
        <X class="mr-1 h-4 w-4" />
        {{ $t('common.close') }}
      </ElButton>
    </template>
  </ElDialog>
</template>

<style scoped>
.preview-dialog :deep(.el-dialog__body) {
  padding: 0;
}

.preview-container {
  min-height: 100%;
  background-color: var(--el-bg-color-page);
}

.preview-widget {
  overflow: hidden;
  background: var(--el-bg-color);
  border-radius: 8px;
  box-shadow: 0 1px 3px rgb(0 0 0 / 10%);
}
</style>
