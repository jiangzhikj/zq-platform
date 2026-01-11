<script setup lang="ts">
import type { WidgetMaterial } from '../store/dashboardDesignStore';

import { computed, ref } from 'vue';

import {
  Activity,
  AreaChart,
  Award,
  BarChart2,
  Bell,
  Calendar,
  CandlestickChart,
  CheckSquare,
  ChevronsLeft,
  ChevronsRight,
  CircleDot,
  Clock,
  CloudSun,
  CreditCard,
  Filter,
  Gauge,
  GitBranch,
  Globe,
  Grid,
  Image,
  Images,
  LayoutDashboard,
  LayoutList,
  LineChart,
  Megaphone,
  PieChart,
  Radar,
  ScatterChart,
  Smile,
  Table,
  Timer,
  TrendingUp,
  Video,
} from '@vben/icons';
import { $t } from '@vben/locales';

import { ElScrollbar } from 'element-plus';

import {
  useDashboardDesignStore,
  widgetMaterials,
} from '../store/dashboardDesignStore';

const store = useDashboardDesignStore();

// 面板是否折叠
const isPanelCollapsed = ref(false);

// 当前激活的分类
const activeCategory = ref('chart');

// 图标映射
const iconMap: Record<string, any> = {
  CreditCard,
  Activity,
  TrendingUp,
  BarChart2,
  PieChart,
  Gauge,
  AreaChart,
  Radar,
  Filter,
  ScatterChart,
  CircleDot,
  CandlestickChart,
  GitBranch,
  CheckSquare,
  Bell,
  Award,
  Grid,
  Smile,
  Calendar,
  Timer,
  Clock,
  CloudSun,
  Images,
  Table,
  Globe,
  Video,
  Image,
  Megaphone,
};

// 分类配置（带图标）
const categories = [
  { key: 'chart', label: $t('dashboard-design.material.category.chart'), icon: LineChart },
  { key: 'widget', label: $t('dashboard-design.material.category.common'), icon: LayoutDashboard },
  { key: 'list', label: $t('dashboard-design.material.category.other'), icon: LayoutList },
];

// 按分类分组
const groupedMaterials = computed(() => {
  const groups: Record<string, WidgetMaterial[]> = {};
  for (const cat of categories) {
    groups[cat.key] = widgetMaterials.filter((m) => m.category === cat.key);
  }
  return groups;
});

// 当前分类的组件列表
const currentMaterials = computed(() => {
  return groupedMaterials.value[activeCategory.value] || [];
});

// 处理拖拽开始
const handleDragStart = (e: DragEvent, material: WidgetMaterial) => {
  store.setDragging(true);
  if (e.dataTransfer) {
    e.dataTransfer.setData('widget-type', material.type);
    e.dataTransfer.effectAllowed = 'copy';
  }
};

// 处理拖拽结束
const handleDragEnd = () => {
  store.setDragging(false);
};

// 点击添加
const handleClick = (material: WidgetMaterial) => {
  store.addWidget(material);
};
</script>

<template>
  <div
    class="material-panel flex h-full"
    :style="{ width: isPanelCollapsed ? '56px' : '262px' }"
  >
    <!-- 左侧导航栏 -->
    <div class="flex w-14 flex-col bg-gray-50 dark:bg-gray-800">
      <!-- 导航按钮 -->
      <button
        v-for="cat in categories"
        :key="cat.key"
        class="nav-btn"
        :class="{ active: activeCategory === cat.key && !isPanelCollapsed }"
        @click="
          activeCategory = cat.key;
          isPanelCollapsed = false;
        "
      >
        <component :is="cat.icon" class="h-4 w-4" />
        <span>{{ cat.label }}</span>
      </button>

      <!-- 占位，将折叠按钮推到底部 -->
      <div class="flex-1"></div>

      <!-- 折叠按钮 -->
      <button
        class="collapse-btn"
        @click="isPanelCollapsed = !isPanelCollapsed"
      >
        <ChevronsLeft v-if="isPanelCollapsed" class="h-4 w-4" />
        <ChevronsRight v-else class="h-4 w-4" />
      </button>
    </div>

    <!-- 右侧内容区域 -->
    <div
      v-show="!isPanelCollapsed"
      class="flex flex-1 flex-col overflow-hidden"
    >
      <ElScrollbar class="flex-1">
        <div class="p-3">
          <div class="grid grid-cols-2 gap-2">
            <div
              v-for="material in currentMaterials"
              :key="material.type"
              class="material-item flex cursor-move flex-col items-center gap-1 rounded-md border border-transparent p-3 transition-all"
              draggable="true"
              @dragstart="(e: DragEvent) => handleDragStart(e, material)"
              @dragend="handleDragEnd"
              @click="handleClick(material)"
            >
              <component
                :is="iconMap[material.icon]"
                class="text-muted-foreground h-6 w-6"
              />
              <span class="text-muted-foreground text-xs">{{
                material.title
              }}</span>
            </div>
          </div>
        </div>
      </ElScrollbar>
    </div>
  </div>
</template>

<style scoped>
.material-panel {
  overflow: hidden;
  background-color: var(--el-bg-color);
  border-radius: 8px;
  transition: width 0.2s ease;
}

.material-item {
  background-color: var(--el-fill-color-lighter);
}

.material-item:hover {
  background-color: var(--el-color-primary-light-9);
  border-color: var(--el-color-primary-light-5);
}

.material-item:active {
  transform: scale(0.95);
}

/* 折叠按钮 */
.collapse-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px 8px;
  color: var(--el-text-color-secondary);
  cursor: pointer;
  background: transparent;
  border: none;
  border-top: 1px solid var(--el-border-color-lighter);
  transition: all 0.2s;
}

.collapse-btn:hover {
  color: var(--el-text-color-primary);
  background-color: var(--el-fill-color-light);
}

/* 左侧导航按钮 */
.nav-btn {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 4px;
  align-items: center;
  justify-content: center;
  padding: 12px 8px;
  font-size: 11px;
  color: var(--el-text-color-secondary);
  cursor: pointer;
  background: transparent;
  border: none;
  transition: all 0.2s;
}

.nav-btn:hover {
  color: var(--el-text-color-primary);
  background-color: var(--el-fill-color-light);
}

.nav-btn.active {
  color: var(--el-color-primary);
  background-color: var(--el-color-primary-light-9);
}

.nav-btn.active::after {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  width: 2px;
  content: '';
  background-color: var(--el-color-primary);
}
</style>
