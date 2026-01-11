<script setup lang="ts">
import type { DashboardWidget } from '#/components/dashboard-design';

import { computed } from 'vue';
import { useRouter } from 'vue-router';

import { Grid, IconifyIcon } from '@vben/icons';

const props = defineProps<{
  widget: DashboardWidget;
}>();

const router = useRouter();

// 计算网格样式
const gridStyle = computed(() => {
  const cols = props.widget.props.columns || 4;
  const rows = props.widget.props.rows || 2;
  return {
    gridTemplateColumns: `repeat(${cols}, minmax(0, 1fr))`,
    gridTemplateRows: `repeat(${rows}, minmax(0, 1fr))`,
  };
});

// 计算总格子数
const totalCells = computed(() => {
  const cols = props.widget.props.columns || 4;
  const rows = props.widget.props.rows || 2;
  return cols * rows;
});

// 获取指定位置的菜单
const getMenuAt = (index: number) => {
  const menus = props.widget.props.menus || [];
  return menus[index] || null;
};

// 图标颜色样式
const iconColorStyle = computed(() => {
  const color = props.widget.props.iconColor;
  return color ? { color } : {};
});

// 点击菜单项
const handleClick = (menu: any) => {
  if (!menu || !menu.path) return;

  // 外链
  if (menu.path.startsWith('http://') || menu.path.startsWith('https://')) {
    window.open(menu.path, '_blank');
    return;
  }

  // 路由跳转
  router.push(menu.path);
};
</script>

<template>
  <div class="quick-links flex h-full flex-col p-3">
    <div class="mb-3 flex items-center gap-2">
      <Grid class="text-muted-foreground h-4 w-4" />
      <span class="text-muted-foreground text-sm font-medium">{{
        widget.props.title
      }}</span>
    </div>
    <div class="grid flex-1 gap-2" :style="gridStyle">
      <template v-for="idx in totalCells" :key="idx">
        <div
          v-if="getMenuAt(idx - 1)"
          class="flex cursor-pointer flex-col items-center justify-center gap-1 rounded-lg p-2 transition-colors hover:bg-gray-100 dark:hover:bg-gray-800"
          @click="handleClick(getMenuAt(idx - 1))"
        >
          <IconifyIcon
            v-if="getMenuAt(idx - 1)?.icon"
            :icon="getMenuAt(idx - 1).icon"
            class="h-6 w-6"
            :class="{ 'text-primary': !widget.props.iconColor }"
            :style="iconColorStyle"
          />
          <Grid
            v-else
            class="h-6 w-6"
            :class="{ 'text-primary': !widget.props.iconColor }"
            :style="iconColorStyle"
          />
          <span
            class="text-muted-foreground w-full truncate text-center text-xs"
            >{{ getMenuAt(idx - 1)?.title }}</span
          >
        </div>
        <div
          v-else
          class="flex flex-col items-center justify-center gap-1 rounded-lg p-2"
        >
          <!-- 空位占位 -->
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped>
/* 背景色由 WidgetRenderer 控制 */
</style>
