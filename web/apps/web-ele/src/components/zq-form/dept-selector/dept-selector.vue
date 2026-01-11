<script lang="ts" setup>
import type { DeptSelectorEmits, DeptSelectorProps } from './types';

import { computed, onMounted, ref, useAttrs, watch } from 'vue';

import { IconifyIcon, Loader, Search } from '@vben/icons';
import { ZqDialog } from '#/components/zq-dialog';
import { $t } from '@vben/locales';

import {
  ElButton,
  ElEmpty,
  ElInput,
  ElOption,
  ElScrollbar,
  ElSelect,
  ElSkeleton,
  ElSkeletonItem,
  ElTag,
} from 'element-plus';

import {
  getDeptByParentApi,
  getDeptsByIds,
  searchDeptApi,
} from '#/api/core/dept';

defineOptions({
  name: 'DeptSelector',
  inheritAttrs: false, // 禁用自动继承，手动控制
});

const props = withDefaults(defineProps<Props>(), {
  multiple: false,
  placeholder: () => $t('ui.placeholder.select') || 'Please select',
  disabled: false,
  clearable: true,
  filterable: true,
});

const emit = defineEmits<DeptSelectorEmits>();

interface Props extends DeptSelectorProps {}

const attrs = useAttrs();

const modalVisible = ref(false);
const departments = ref<any[]>([]);
const selectedDepts = ref<Set<string>>(
  new Set(
    Array.isArray(props.modelValue)
      ? props.modelValue
      : (props.modelValue
        ? [props.modelValue]
        : []),
  ),
);
// 临时选择（用于 modal 中的选择，未确认前）
const tempSelectedDepts = ref<Set<string>>(new Set());
const deptLoading = ref(false);
const searchText = ref('');
const expandedDeptIds = ref<Set<string>>(new Set());
const loadingDeptIds = ref<Set<string>>(new Set());
// 搜索相关
const searchResults = ref<any[]>([]);
const isSearching = ref(false);
// 标记是否已加载过部门数据
const hasLoadedDepts = ref(false);

// 计算显示值（只显示已确认的值）
const displayValue = computed({
  get() {
    if (selectedDepts.value.size === 0) return undefined;
    if (props.multiple) {
      return [...selectedDepts.value];
    }
    return [...selectedDepts.value][0];
  },
  set(_value) {
    // ElSelect 会改变这个值，但我们不需要处理
  },
});

// 获取部门的完整路径（从根节点到该部门）
const getDeptPath = (deptId: string): string => {
  const deptMap = new Map();
  const parentMap = new Map();

  function buildMaps(nodes: any[], parentId: null | string = null) {
    nodes.forEach((node) => {
      deptMap.set(node.id, node);
      parentMap.set(node.id, parentId);
      if (node.children) {
        buildMaps(node.children, node.id);
      }
    });
  }

  // 同时从 departments 和 searchResults 构建映射
  // 这样可以处理搜索结果中的深层部门
  buildMaps(departments.value);
  if (searchResults.value.length > 0) {
    buildMaps(searchResults.value);
  }

  const path: string[] = [];
  let currentId: null | string = deptId;

  while (currentId) {
    const dept = deptMap.get(currentId);
    if (dept && dept.id !== '0') {
      // 跳过根节点"全部部门"
      path.unshift(dept.name);
    }
    currentId = parentMap.get(currentId);
  }

  return path.join(' / ');
};

// 获取已选部门的完整路径信息
const selectedDeptsWithPath = computed(() => {
  const result = [];
  const seenIds = new Set<string>(); // 用于去重

  for (const deptId of selectedDepts.value) {
    // 避免重复添加
    if (seenIds.has(deptId)) continue;

    seenIds.add(deptId);
    result.push({
      id: deptId,
      display: getDeptPath(deptId),
    });
  }
  return result;
});

// 获取临时选择部门的完整路径信息
const tempSelectedDeptsWithPath = computed(() => {
  const result = [];
  const seenIds = new Set<string>(); // 用于去重

  for (const deptId of tempSelectedDepts.value) {
    // 避免重复添加
    if (seenIds.has(deptId)) continue;

    seenIds.add(deptId);
    result.push({
      id: deptId,
      display: getDeptPath(deptId),
    });
  }
  return result;
});

// 加载顶级部门数据
const loadDepartments = async () => {
  // 如果已经加载过根节点，则不重复加载
  if (departments.value.length > 0 && departments.value[0].id === '0') {
    return;
  }

  try {
    deptLoading.value = true;
    const result = await getDeptByParentApi(null);

    // 添加"全部部门"根节点
    const rootNode = {
      id: '0',
      name: $t('system.user.allDept') || 'All Departments',
      children: Array.isArray(result) ? result : [],
      parent_id: null,
      status: 1,
    };

    departments.value = [rootNode];
    expandedDeptIds.value.add('0');

    deptLoading.value = false;
  } catch (error) {
    console.error('Failed to load departments:', error);
    deptLoading.value = false;
  }
};

// 根据ID加载特定部门信息（用于编辑时显示已选但未加载的部门）
// 这个函数用于加载选中部门的路径信息，并将其合并到现有的部门树中
const loadDepartmentsByIds = async (ids: string[]) => {
  if (!ids || ids.length === 0) return;

  try {
    // 调用批量获取部门API，返回包含目标部门及其所有祖先的树形结构
    const result = await getDeptsByIds(ids);

    if (result && result.length > 0) {
      // 合并数据到现有的部门树中
      // 需要将获取的树形数据合并到 departments 中
      const mergeTree = (existingNodes: any[], newNodes: any[]) => {
        for (const newNode of newNodes) {
          const existingNode = existingNodes.find((n) => n.id === newNode.id);
          if (existingNode) {
            // 节点已存在，合并子节点
            if (newNode.children && newNode.children.length > 0) {
              if (!existingNode.children) {
                existingNode.children = [];
              }
              mergeTree(existingNode.children, newNode.children);
            }
          } else {
            // 新节点，直接添加
            existingNodes.push(newNode);
          }
        }
      };

      // 确保根节点存在，然后合并数据
      if (departments.value.length > 0 && departments.value[0].id === '0') {
        // 根节点已存在，直接合并
        if (!departments.value[0].children) {
          departments.value[0].children = [];
        }
        mergeTree(departments.value[0].children, result);
      } else {
        // 根节点不存在，创建根节点并添加数据
        const rootNode = {
          id: '0',
          name: $t('system.user.allDept') || 'All Departments',
          children: result,
          parent_id: null,
          status: 1,
        };
        departments.value = [rootNode];
        expandedDeptIds.value.add('0');
      }
    }

    hasLoadedDepts.value = true;
  } catch (error) {
    console.error('Failed to load departments by ids:', error);
  }
};

// 加载子部门（懒加载）
const loadChildrenDepts = async (parentId: string) => {
  try {
    loadingDeptIds.value.add(parentId);
    const data = await getDeptByParentApi(parentId);

    // 更新树数据中的子部门
    function updateNodeChildren(nodes: any[], targetId: string): boolean {
      for (const node of nodes) {
        if (node.id === targetId) {
          node.children = Array.isArray(data) ? data : [];
          return true;
        }
        if (
          node.children &&
          node.children.length > 0 &&
          updateNodeChildren(node.children, targetId)
        ) {
          return true;
        }
      }
      return false;
    }

    updateNodeChildren(departments.value, parentId);
  } catch (error) {
    console.error('Failed to load child departments:', error);
  } finally {
    loadingDeptIds.value.delete(parentId);
  }
};

// 检查部门是否有子部门
const hasChildren = (dept: any): boolean => {
  if (dept.child_count && typeof dept.child_count === 'number') {
    return dept.child_count > 0;
  }
  if (!dept.children) return false;
  return dept.children.length > 0;
};

// 切换部门展开/折叠
const toggleDeptExpanded = async (dept: any) => {
  if (expandedDeptIds.value.has(dept.id)) {
    expandedDeptIds.value.delete(dept.id);
  } else {
    expandedDeptIds.value.add(dept.id);
    // 如果子部门未加载，则加载
    if (!dept.children || dept.children.length === 0) {
      await loadChildrenDepts(dept.id);
    }
  }
};

// 部门树过滤：如果有搜索结果则使用搜索结果，否则使用完整树
const filteredDepts = computed(() => {
  if (searchText.value.trim() && searchResults.value.length > 0) {
    return searchResults.value;
  }
  return departments.value;
});

// 自动展开搜索结果中的所有节点
const autoExpandSearchResults = (nodes: any[]) => {
  nodes.forEach((node) => {
    expandedDeptIds.value.add(node.id);
    if (node.children && node.children.length > 0) {
      autoExpandSearchResults(node.children);
    }
  });
};

// 防抖搜索定时器
let searchTimer: null | ReturnType<typeof setTimeout> = null;

// 监听搜索文本变化，执行后端搜索
watch(searchText, (newVal) => {
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
      const results = await searchDeptApi(newVal);
      searchResults.value = results || [];
      // 自动展开搜索结果中的所有节点，显示完整路径
      if (results && results.length > 0) {
        autoExpandSearchResults(results);
      }
    } catch (error) {
      console.error('搜索部门失败:', error);
      searchResults.value = [];
    } finally {
      isSearching.value = false;
    }
  }, 300);
});

// 渲染树列表（扁平化）
const renderTreeList = (nodes: any[], level: number = 0): any[] => {
  return nodes.flatMap((node) => [
    { node, level, isNode: true },
    ...(expandedDeptIds.value.has(node.id) &&
    node.children &&
    node.children.length > 0
      ? renderTreeList(node.children, level + 1)
      : []),
  ]);
};

const flattenedTree = computed(() => renderTreeList(filteredDepts.value));

// 处理部门选择
const handleDeptSelect = (deptId: string) => {
  if (props.multiple) {
    if (tempSelectedDepts.value.has(deptId)) {
      tempSelectedDepts.value.delete(deptId);
    } else {
      tempSelectedDepts.value.add(deptId);
    }
  } else {
    // 单选模式
    tempSelectedDepts.value.clear();
    tempSelectedDepts.value.add(deptId);
  }
};

// 打开modal
const openModal = async () => {
  if (props.disabled) return;
  modalVisible.value = true;
};

// 打开modal后加载数据
const handleModalOpened = async () => {
  // 初始化临时选择为已选择的值
  tempSelectedDepts.value = new Set(selectedDepts.value);

  if (departments.value.length === 0) {
    await loadDepartments();
  }
};

// 确认选择
const handleConfirm = () => {
  // 将临时选择的值保存到 selectedDepts（已确认）
  selectedDepts.value = new Set(tempSelectedDepts.value);

  const value = props.multiple
    ? [...selectedDepts.value]
    : (selectedDepts.value.size > 0
      ? [...selectedDepts.value][0]
      : '');

  emit('update:modelValue', value);
  emit('change', value);
  modalVisible.value = false;
};

// 清除选择
const handleClear = (e?: MouseEvent) => {
  if (e) {
    e.stopPropagation();
  }
  tempSelectedDepts.value.clear();
  selectedDepts.value.clear();
  const emptyValue = props.multiple ? [] : '';
  emit('update:modelValue', emptyValue);
  emit('change', emptyValue);
};

// 删除单个选中项（多选模式下点击标签删除按钮）
const handleRemoveTag = (deptId: string) => {
  selectedDepts.value.delete(deptId);
  const value = props.multiple ? [...selectedDepts.value] : '';
  emit('update:modelValue', value);
  emit('change', value);
};

// 监听外部 modelValue 变化
const updateInternalValue = () => {
  selectedDepts.value.clear();
  tempSelectedDepts.value.clear();
  if (Array.isArray(props.modelValue)) {
    props.modelValue.forEach((v) => selectedDepts.value.add(v));
  } else if (props.modelValue) {
    selectedDepts.value.add(props.modelValue);
  }
  // 打开 modal 时初始化临时选择
  if (modalVisible.value) {
    tempSelectedDepts.value = new Set(selectedDepts.value);
  }
};

// 监听 modelValue 变化，如果有值且部门数据未加载，则加载
watch(
  () => props.modelValue,
  async (newValue) => {
    updateInternalValue();

    // 如果有选中值且部门数据未加载，则需要加载部门数据
    if (
      ((Array.isArray(newValue) && newValue.length > 0) ||
        (typeof newValue === 'string' && newValue)) &&
      !hasLoadedDepts.value
    ) {
      // 先加载完整的根级部门树
      await loadDepartments();

      // 然后加载选中部门的路径信息，用于展开和标记
      const ids = Array.isArray(newValue) ? newValue : [newValue];
      await loadDepartmentsByIds(ids);
    }
  },
  { immediate: true },
);

// 组件挂载时，如果有初始值，则加载部门数据
onMounted(async () => {
  if (
    (Array.isArray(props.modelValue) && props.modelValue.length > 0) ||
    (typeof props.modelValue === 'string' && props.modelValue)
  ) {
    // 先加载完整的根级部门树
    await loadDepartments();

    // 然后加载选中部门的路径信息，用于展开和标记
    const ids = Array.isArray(props.modelValue)
      ? props.modelValue
      : [props.modelValue];
    await loadDepartmentsByIds(ids);
  }
});

defineExpose({
  openModal,
});
</script>

<template>
  <div class="dept-selector">
    <!-- 选择框 -->
    <div
      class="dept-selector-input"
      :class="{ disabled, loading: deptLoading }"
    >
      <ElSelect
        v-bind="attrs"
        v-model="displayValue"
        :placeholder="
          deptLoading ? $t('common.loading') || 'Loading...' : placeholder
        "
        :disabled="disabled || deptLoading"
        :clearable="clearable && selectedDepts.size > 0"
        :multiple="multiple"
        readonly
        @click="openModal"
        @clear="() => handleClear()"
        @remove-tag="handleRemoveTag"
      >
        <ElOption
          v-for="item in selectedDeptsWithPath"
          :key="item.id"
          :label="item.display"
          :value="item.id"
        />
      </ElSelect>

      <!-- Loading 提示 -->
      <div v-if="deptLoading" class="loading-indicator">
        <Loader class="size-4 animate-spin" />
        <span class="ml-2 text-xs text-gray-500">{{
          $t('common.loading') || 'Loading...'
        }}</span>
      </div>
    </div>

    <!-- Modal -->
    <ZqDialog
      v-model="modalVisible"
      :title="$t('system.user.selectDept') || 'Select Departments'"
      width="45%"
      :show-footer="true"
      :show-fullscreen-button="false"
      @opened="handleModalOpened"
    >
      <div class="dept-selector-content">
        <!-- 顶部：已选项（左侧）+ 搜索框（右侧） -->
        <div class="dept-selector-header-row">
          <div class="header-middle">
            <div
              v-if="tempSelectedDeptsWithPath.length > 0"
              class="selected-tags"
            >
              <ElTag
                v-for="item of tempSelectedDeptsWithPath"
                :key="item.id"
                closable
                type="info"
                size="small"
                @close="
                  () => {
                    tempSelectedDepts.delete(item.id);
                  }
                "
              >
                {{ item.display }}
              </ElTag>
            </div>
            <span v-else class="empty-text">-</span>
          </div>

          <!-- 搜索框（右侧） -->
          <div v-if="filterable" class="header-search">
            <ElInput
              v-model="searchText"
              :placeholder="$t('common.search') || 'Search'"
              clearable
              :prefix-icon="Search"
            />
          </div>
        </div>

        <!-- 部门树列表 -->
        <ElScrollbar class="dept-selector-tree" :distance="40">
          <ElSkeleton :loading="deptLoading || isSearching" animated :count="8">
            <template #template>
              <div class="dept-selector-tree-content">
                <div v-for="i in 8" :key="i" class="dept-skeleton-item">
                  <ElSkeletonItem
                    variant="text"
                    style="width: 100%; height: 40px; margin: 8px 0"
                  />
                </div>
              </div>
            </template>
            <template #default>
              <div class="dept-selector-tree-content">
                <ElEmpty
                  v-if="flattenedTree.length === 0"
                  :description="$t('common.noData') || 'No Data'"
                />
                <div v-else class="dept-list">
                  <div
                    v-for="(item, index) in flattenedTree"
                    :key="`${item.node.id}-${index}`"
                    class="dept-item"
                    :class="[
                      tempSelectedDepts.has(item.node.id)
                        ? 'bg-primary/15 dark:bg-accent text-primary'
                        : 'hover:bg-[var(--el-fill-color-light)]',
                    ]"
                    :style="{
                      paddingLeft: `calc(12px + ${item.level * 20}px)`,
                    }"
                    @click="handleDeptSelect(item.node.id)"
                  >
                    <!-- 展开/折叠按钮 -->
                    <div v-if="hasChildren(item.node)" class="dept-toggle">
                      <div
                        class="toggle-icon"
                        @click.stop="toggleDeptExpanded(item.node)"
                      >
                        <IconifyIcon
                          v-if="!loadingDeptIds.has(item.node.id)"
                          icon="ep:caret-right"
                          class="size-4 transform transition-transform"
                          :class="
                            expandedDeptIds.has(item.node.id) ? 'rotate-90' : ''
                          "
                        />
                        <Loader v-else class="size-4 animate-spin" />
                      </div>
                    </div>
                    <div v-else class="dept-toggle-spacer"></div>

                    <!-- 部门名称 -->
                    <div class="dept-name">{{ item.node.name }}</div>
                  </div>
                </div>
              </div>
            </template>
          </ElSkeleton>
        </ElScrollbar>
      </div>

      <template #footer>
        <div class="modal-footer">
          <div class="footer-left">
            <span class="selected-count">
              {{ tempSelectedDepts.size }}
              {{ $t('common.selected') || 'selected' }}
            </span>
            <ElButton
              v-if="tempSelectedDepts.size > 0"
              link
              type="danger"
              size="small"
              @click="() => tempSelectedDepts.clear()"
            >
              {{ $t('common.clear') || 'Clear' }}
            </ElButton>
          </div>
          <div class="footer-right">
            <ElButton @click="modalVisible = false">
              {{ $t('common.cancel') || 'Cancel' }}
            </ElButton>
            <ElButton type="primary" @click="handleConfirm">
              {{ $t('common.confirm') || 'Confirm' }}
            </ElButton>
          </div>
        </div>
      </template>
    </ZqDialog>
  </div>
</template>

<style lang="scss" scoped>
.dept-selector {
  width: 100%;

  &-input {
    position: relative;
    cursor: pointer;

    &.disabled {
      cursor: not-allowed;
      opacity: 0.6;
    }

    &.loading {
      cursor: wait;
    }

    :deep(.el-input) {
      &.is-disabled {
        background-color: var(--background-deep, #f5f7fa);
      }
    }

    .loading-indicator {
      position: absolute;
      top: 50%;
      right: 10px;
      z-index: 10;
      display: flex;
      gap: 6px;
      align-items: center;
      font-size: 12px;
      color: var(--el-color-info);
      pointer-events: none;
      transform: translateY(-50%);

      .size-4 {
        width: 16px;
        height: 16px;
      }
    }
  }


  &-content {
    display: flex;
    flex-direction: column;
    gap: 0;
    height: 500px;
    padding: 0;
    overflow: hidden;
    background-color: hsl(var(--background));
    border: 1px solid hsl(var(--border));
    border-radius: var(--radius);
    box-shadow: 0 1px 3px hsl(var(--border) / 12%);
  }

  &-header-row {
    display: flex;
    flex-shrink: 0;
    gap: 12px;
    align-items: center;
    padding: 12px 16px;
    background: linear-gradient(
      90deg,
      hsl(var(--background)) 0%,
      hsl(var(--background-deep) / 30%) 100%
    );
    border-bottom: 1px solid hsl(var(--border));

    .header-middle {
      display: flex;
      flex: 1;
      gap: 8px;
      align-items: center;
      min-width: 80px;
      max-height: 40px;
      overflow-y: auto;

      .selected-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        align-items: center;

        :deep(.el-tag) {
          height: 24px;
          font-size: 12px;
          line-height: 22px;
        }
      }

      .empty-text {
        font-size: 12px;
        color: hsl(var(--muted-foreground));
        white-space: nowrap;
      }
    }

    .header-search {
      flex-shrink: 0;
      width: 160px;

      :deep(.el-input) {
        font-size: 14px;
      }
    }
  }

  &-tree {
    flex: 1;
    overflow-y: auto;
    border-top: none;
  }

  &-tree-content {
    display: flex;
    flex: 1;
    flex-direction: column;
    width: 100%;
    padding: 8px 10px;

    .dept-list {
      display: flex;
      flex-direction: column;
    }

    .dept-item {
      display: flex;
      align-items: center;
      height: 42px;
      padding: 0 12px;
      margin: 1px 0;
      cursor: pointer;
      border-radius: 8px;
      transition: all 0.2s ease;

      .dept-toggle {
        display: flex;
        flex-shrink: 0;
        align-items: center;
        justify-content: center;
        width: 20px;
        height: 20px;
        margin-right: 4px;

        .toggle-icon {
          display: flex;
          align-items: center;
          justify-content: center;
          color: currentcolor;
          cursor: pointer;
          transition: transform 0.2s ease;

          &:hover {
            color: var(--primary, #409eff);
          }
        }
      }

      .dept-toggle-spacer {
        flex-shrink: 0;
        width: 20px;
        margin-right: 4px;
      }

      .dept-name {
        flex: 1;
        overflow: hidden;
        text-overflow: ellipsis;
        font-size: 14px;
        white-space: nowrap;
        transition: color 0.2s ease;
      }
    }
  }
}

.modal-footer {
  display: flex;
  gap: 8px;
  align-items: center;
  justify-content: space-between;

  .footer-left {
    display: flex;
    gap: 8px;
    align-items: center;
  }

  .footer-right {
    display: flex;
    gap: 8px;
    align-items: center;
    margin-left: auto;
  }
}

.dept-skeleton-item {
  box-sizing: border-box;
  display: flex;
  align-items: center;
  width: 100%;
  padding: 8px 12px;
}
</style>
