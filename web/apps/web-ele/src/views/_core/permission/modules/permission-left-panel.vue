<script lang="ts" setup>
import type { MenuTreeNode } from '#/api/core/menu';

import { computed, onMounted, ref, watch } from 'vue';

import { IconifyIcon, Loader, Search } from '@vben/icons';
import { $t } from '@vben/locales';

import {
  ElCard,
  ElInput,
  ElMessage,
  ElSkeleton,
  ElSkeletonItem,
} from 'element-plus';

import { getAllMenuTreeApi, searchMenuApi } from '#/api/core/menu';

const emit = defineEmits<{
  select: [menuId: string, menuName?: string];
}>();

const treeData = ref<MenuTreeNode[]>([]);
const loading = ref(false);
const selectedMenuId = ref<string>();
const searchKeyword = ref<string>('');
const hoveredMenuId = ref<string>();
const expandedMenuIds = ref<Set<string>>(new Set());
const loadingMenuIds = ref<Set<string>>(new Set());
const searchResults = ref<MenuTreeNode[]>([]);
const isSearching = ref(false);

let searchTimer: null | ReturnType<typeof setTimeout> = null;

/**
 * 加载完整菜单树数据
 */
async function fetchMenuList() {
  try {
    loading.value = true;
    const data = await getAllMenuTreeApi(false); // 不使用缓存，确保获取最新数据
    treeData.value = Array.isArray(data) ? data : [];

    // 自动展开第一级
    if (treeData.value.length > 0) {
      treeData.value.forEach((menu) => {
        expandedMenuIds.value.add(menu.id);
      });

      // 自动选中第一个菜单
      if (!selectedMenuId.value && treeData.value.length > 0) {
        const firstMenu = treeData.value[0];
        if (firstMenu) {
          selectedMenuId.value = firstMenu.id;
          emit('select', firstMenu.id);
        }
      }
    }
  } catch (error) {
    console.error($t('permission.loadMenuFailed'), error);
    ElMessage.error($t('permission.loadMenuFailed'));
  } finally {
    loading.value = false;
  }
}

/**
 * 加载子菜单（懒加载）
 */
async function loadChildren(parentId: string) {
  try {
    loadingMenuIds.value.add(parentId);
    // 由于已经有完整树，这里不再需要单独加载子菜单
    // 但保持此方法以便将来扩展
  } catch (error) {
    console.error($t('permission.loadSubMenuFailed'), error);
    ElMessage.error($t('permission.loadSubMenuFailed'));
  } finally {
    loadingMenuIds.value.delete(parentId);
  }
}

/**
 * 切换节点展开/折叠
 */
async function toggleNodeExpanded(menu: MenuTreeNode) {
  if (expandedMenuIds.value.has(menu.id)) {
    expandedMenuIds.value.delete(menu.id);
  } else {
    expandedMenuIds.value.add(menu.id);

    // 如果子菜单未加载，则加载
    if (!menu.children || menu.children.length === 0) {
      await loadChildren(menu.id);
    }
  }
}

/**
 * 选择菜单
 */
function onMenuSelect(menu: MenuTreeNode) {
  selectedMenuId.value = menu.id;
  emit('select', menu.id, menu.name);
}

/**
 * 检查菜单是否有子菜单
 */
function hasChildren(menu: MenuTreeNode): boolean {
  // 首先检查 child_count 字段（后端返回的子菜单数量）
  if ('child_count' in menu && typeof menu.child_count === 'number') {
    return menu.child_count > 0;
  }
  // 如果没有 child_count 字段，则检查 children 属性
  if (!menu.children) {
    return false; // 没有信息表示没有子菜单
  }
  return menu.children.length > 0;
}

/**
 * 自动展开搜索结果中的所有节点
 */
function autoExpandSearchResults(nodes: MenuTreeNode[]) {
  nodes.forEach((node) => {
    expandedMenuIds.value.add(node.id);
    if (node.children && node.children.length > 0) {
      autoExpandSearchResults(node.children);
    }
  });
}

/**
 * 监听搜索文本变化，执行后端搜索
 */
watch(searchKeyword, (newVal) => {
  // 清除之前的定时器
  if (searchTimer) {
    clearTimeout(searchTimer);
  }

  if (!newVal.trim()) {
    searchResults.value = [];
    isSearching.value = false;
    return;
  }

  // 设置新的防抖定时器
  searchTimer = setTimeout(async () => {
    isSearching.value = true;
    try {
      const results = await searchMenuApi(newVal);
      searchResults.value = results || [];
      // 自动展开搜索结果中的所有节点，显示完整路径
      if (searchResults.value && searchResults.value.length > 0) {
        autoExpandSearchResults(searchResults.value);
      }
    } catch (error) {
      console.error($t('permission.searchMenuFailed'), error);
      searchResults.value = [];
    } finally {
      isSearching.value = false;
    }
  }, 300);
});

/**
 * 过滤树数据：如果有搜索结果则使用搜索结果，否则使用完整树
 */
const filteredTreeData = computed(() => {
  if (searchKeyword.value.trim() && searchResults.value.length > 0) {
    return searchResults.value;
  }
  return treeData.value;
});

/**
 * 渲染树形列表
 */
const renderTreeList = (nodes: MenuTreeNode[], level: number = 0): any[] => {
  return nodes.flatMap((node) => [
    { node, level, isNode: true },
    ...(expandedMenuIds.value.has(node.id) &&
    node.children &&
    node.children.length > 0
      ? renderTreeList(node.children, level + 1)
      : []),
  ]);
};

const flattenedTree = computed(() => renderTreeList(filteredTreeData.value));

onMounted(() => {
  fetchMenuList();
});
</script>

<template>
  <ElCard
    style="border: none"
    class="mr-[10px] flex h-full flex-col"
    shadow="never"
    :body-style="{
      padding: '20px',
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
    }"
  >
    <!-- 搜索和添加区域 -->
    <div class="mb-4 flex gap-2">
      <ElInput
        v-model="searchKeyword"
        :placeholder="$t('permission.searchMenu')"
        clearable
        :prefix-icon="Search"
      />
    </div>

    <!-- 菜单树列表 -->
    <div class="flex-1 overflow-auto">
      <ElSkeleton :loading="loading || isSearching" animated :count="8">
        <template #template>
          <div class="space-y-1">
            <div v-for="i in 8" :key="i" class="menu-skeleton-item">
              <ElSkeletonItem
                variant="text"
                style="width: 100%; height: 40px"
              />
            </div>
          </div>
        </template>
        <template #default>
          <div class="space-y-1">
            <div
              v-for="(item, index) in flattenedTree"
              :key="`${item.node.id}-${index}`"
              class="flex h-[42px] cursor-pointer items-center justify-between rounded-[8px] px-3 transition-colors"
              :class="[
                selectedMenuId === item.node.id
                  ? 'bg-primary/15 dark:bg-accent text-primary'
                  : 'hover:bg-[var(--el-fill-color-light)]',
              ]"
              :style="{ paddingLeft: `calc(12px + ${item.level * 20}px)` }"
              @mouseenter="hoveredMenuId = item.node.id"
              @mouseleave="hoveredMenuId = undefined"
              @click="onMenuSelect(item.node)"
            >
              <!-- 菜单名称和展开/折叠按钮 -->
              <div class="flex min-w-0 flex-1 items-center gap-1.5">
                <!-- 展开/折叠按钮 -->
                <div
                  v-if="hasChildren(item.node)"
                  class="hover:text-primary flex w-4 flex-shrink-0 cursor-pointer items-center justify-center"
                  @click.stop="toggleNodeExpanded(item.node)"
                >
                  <Loader
                    v-if="loadingMenuIds.has(item.node.id)"
                    class="size-4 animate-spin"
                  />
                  <IconifyIcon
                    v-else
                    icon="ep:caret-right"
                    class="size-4 transform transition-transform"
                    :class="
                      expandedMenuIds.has(item.node.id) ? 'rotate-90' : ''
                    "
                  />
                </div>
                <div v-else class="w-4 flex-shrink-0"></div>

                <!-- 菜单图标 -->
                <div class="text-primary size-4 flex-shrink-0">
                  <IconifyIcon
                    :icon="item.node.icon || 'carbon:circle-dash'"
                    class="size-full"
                  />
                </div>

                <!-- 菜单名称 -->
                <div
                  class="truncate text-sm"
                  :title="
                    item.node.title ? $t(item.node.title) : item.node.name
                  "
                >
                  {{ item.node.title ? $t(item.node.title) : item.node.name }}
                </div>
              </div>
            </div>
          </div>
        </template>
      </ElSkeleton>
    </div>
  </ElCard>
</template>

<style scoped>
/* 输入框前置图标样式 */
:deep(.el-input__icon) {
  cursor: pointer;
}

/* 骨架屏样式 */
.menu-skeleton-item {
  box-sizing: border-box;
  display: flex;
  align-items: center;
  width: 100%;
  padding: 8px 12px;
}
</style>
