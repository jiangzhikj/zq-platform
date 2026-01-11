<script setup lang="ts">
import type {
  DataSourceConfig,
  WidgetStyle,
} from '../store/dashboardDesignStore';

import type { DataSourceSimple } from '#/api/core/data-source';
import type { MenuItem } from '#/components/zq-form/zq-menu-selector/types';

import { computed, ref, watch } from 'vue';

import {
  ChevronsLeft,
  ChevronsRight,
  Database,
  IconifyIcon,
  Palette,
  Plus,
  Settings,
  Trash2,
} from '@vben/icons';
import { $t } from '@vben/locales';

import {
  ElButton,
  ElColorPicker,
  ElDatePicker,
  ElDivider,
  ElForm,
  ElFormItem,
  ElInput,
  ElInputNumber,
  ElOption,
  ElRadioButton,
  ElRadioGroup,
  ElScrollbar,
  ElSelect,
  ElSwitch,
  ElTag,
} from 'element-plus';

import { getAllDataSourceApi } from '#/api/core/data-source';
import FileSelector from '#/components/zq-form/file-selector/file-selector.vue';
import { ImageSelector } from '#/components/zq-form/image-selector';
import { ZqMenuSelector } from '#/components/zq-form/zq-menu-selector';

import {
  defaultWidgetStyle,
  useDashboardDesignStore,
  widgetMaterials,
} from '../store/dashboardDesignStore';
import { getWidgetFieldTargets } from '../utils/dataFetcher';

const store = useDashboardDesignStore();

// 当前选中的 widget
const activeWidget = computed(() => store.activeWidget);

// 当前激活的 Tab
const activeTab = ref('basic');

// 面板是否折叠
const isPanelCollapsed = ref(false);

// 获取 widget 材料信息（保留以备后用）
const _widgetMaterial = computed(() => {
  if (!activeWidget.value) return null;
  return widgetMaterials.find((m) => m.type === activeWidget.value!.type);
});
void _widgetMaterial.value;

// 本地表单数据
const formData = ref<Record<string, any>>({});

// 监听 activeWidget 变化，同步表单数据
watch(
  () => activeWidget.value,
  (widget) => {
    formData.value = widget
      ? {
          title: widget.title || '',
          ...widget.props,
        }
      : {};
  },
  { immediate: true, deep: true },
);

// 更新标题
const updateTitle = (value: string) => {
  if (activeWidget.value) {
    store.updateWidgetTitle(activeWidget.value.id, value);
  }
};

// 更新属性
const updateProps = (key: string, value: any) => {
  if (activeWidget.value) {
    store.updateWidgetProps(activeWidget.value.id, { [key]: value });
  }
};

// 图标选项
const iconOptions = [
  { label: $t('dashboard-design.attribute.iconOptions.trending'), value: 'TrendingUp' },
  { label: $t('dashboard-design.attribute.iconOptions.creditCard'), value: 'CreditCard' },
  { label: $t('dashboard-design.attribute.iconOptions.users'), value: 'Users' },
  { label: $t('dashboard-design.attribute.iconOptions.activity'), value: 'Activity' },
  { label: $t('dashboard-design.attribute.iconOptions.bell'), value: 'Bell' },
  { label: $t('dashboard-design.attribute.iconOptions.award'), value: 'Award' },
];

// 进度条状态选项
const progressStatusOptions = [
  { label: $t('dashboard-design.attribute.progressStatus.default'), value: '' },
  { label: $t('dashboard-design.attribute.progressStatus.success'), value: 'success' },
  { label: $t('dashboard-design.attribute.progressStatus.warning'), value: 'warning' },
  { label: $t('dashboard-design.attribute.progressStatus.exception'), value: 'exception' },
];

// 颜色主题选项
const colorThemeOptions = [
  {
    label: $t('dashboard-design.attribute.colorTheme.default'),
    value: 'default',
    colors: ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de'],
  },
  {
    label: $t('dashboard-design.attribute.colorTheme.fresh'),
    value: 'fresh',
    colors: ['#37a2da', '#32c5e9', '#67e0e3', '#9fe6b8', '#ffdb5c'],
  },
  {
    label: $t('dashboard-design.attribute.colorTheme.business'),
    value: 'business',
    colors: ['#2ec7c9', '#b6a2de', '#5ab1ef', '#ffb980', '#d87a80'],
  },
  {
    label: $t('dashboard-design.attribute.colorTheme.tech'),
    value: 'tech',
    colors: ['#00d4ff', '#00ff88', '#ff6b6b', '#ffd93d', '#6bcb77'],
  },
  {
    label: $t('dashboard-design.attribute.colorTheme.warm'),
    value: 'warm',
    colors: ['#ff6b6b', '#feca57', '#ff9ff3', '#54a0ff', '#5f27cd'],
  },
];

// 数据源列表
const dataSourceList = ref<DataSourceSimple[]>([]);
const loadingDataSource = ref(false);

// 加载数据源列表
async function loadDataSourceList() {
  if (dataSourceList.value.length > 0) return;
  try {
    loadingDataSource.value = true;
    const data = await getAllDataSourceApi();
    dataSourceList.value = data || [];
  } catch (error) {
    console.error($t('dashboard-design.loadDataError'), error);
  } finally {
    loadingDataSource.value = false;
  }
}

// 结果类型标签映射
const resultTypeLabelMap: Record<string, string> = {
  list: $t('dashboard-design.attribute.resultType.list'),
  tree: $t('dashboard-design.attribute.resultType.tree'),
  object: $t('dashboard-design.attribute.resultType.object'),
  value: $t('dashboard-design.attribute.resultType.value'),
  'chart-axis': $t('dashboard-design.attribute.resultType.chartAxis'),
  'chart-pie': $t('dashboard-design.attribute.resultType.chartPie'),
  'chart-gauge': $t('dashboard-design.attribute.resultType.chartGauge'),
  'chart-radar': $t('dashboard-design.attribute.resultType.chartRadar'),
  'chart-scatter': $t('dashboard-design.attribute.resultType.chartScatter'),
  'chart-heatmap': $t('dashboard-design.attribute.resultType.chartHeatmap'),
};

// 获取结果类型标签
function getResultTypeLabel(resultType: string): string {
  return resultTypeLabelMap[resultType] || resultType;
}

// 数据源表单
const dataSourceForm = ref<DataSourceConfig>({
  type: 'static',
  apiUrl: '',
  apiMethod: 'GET',
  dataPath: '',
  refreshInterval: 0,
  refreshEnabled: false,
  fieldMappings: [],
});

// 监听 activeWidget 变化，同步数据源表单
watch(
  () => activeWidget.value?.dataSource,
  (ds) => {
    if (ds) {
      dataSourceForm.value = {
        type: ds.type || 'static',
        dataSourceCode: ds.dataSourceCode || '',
        apiUrl: ds.apiUrl || '',
        apiMethod: ds.apiMethod || 'GET',
        apiHeaders: ds.apiHeaders || {},
        apiParams: ds.apiParams || {},
        apiBody: ds.apiBody || {},
        dataPath: ds.dataPath || '',
        refreshInterval: ds.refreshInterval || 0,
        refreshEnabled: ds.refreshEnabled || false,
        fieldMappings: ds.fieldMappings || [],
      };
      // 如果是数据源类型，加载数据源列表
      if (ds.type === 'dataSource') {
        loadDataSourceList();
      }
    } else {
      dataSourceForm.value = {
        type: 'static',
        dataSourceCode: '',
        apiUrl: '',
        apiMethod: 'GET',
        dataPath: '',
        refreshInterval: 0,
        refreshEnabled: false,
        fieldMappings: [],
      };
    }
  },
  { immediate: true },
);

// 获取当前组件支持的字段映射目标
const fieldTargets = computed(() => {
  if (!activeWidget.value) return [];
  return getWidgetFieldTargets(activeWidget.value.type);
});

// 更新数据源配置
const updateDataSource = () => {
  if (!activeWidget.value) return;
  store.updateWidgetDataSource(activeWidget.value.id, {
    ...dataSourceForm.value,
  });
};

// 添加字段映射
const addFieldMapping = () => {
  if (!dataSourceForm.value.fieldMappings) {
    dataSourceForm.value.fieldMappings = [];
  }
  dataSourceForm.value.fieldMappings.push({ source: '', target: '' });
  updateDataSource();
};

// 删除字段映射
const removeFieldMapping = (index: number) => {
  dataSourceForm.value.fieldMappings?.splice(index, 1);
  updateDataSource();
};

// 更新字段映射
const updateFieldMapping = (
  index: number,
  field: 'source' | 'target',
  value: string,
) => {
  if (dataSourceForm.value.fieldMappings?.[index]) {
    dataSourceForm.value.fieldMappings[index][field] = value;
    updateDataSource();
  }
};

// 样式表单
const styleForm = ref<WidgetStyle>({ ...defaultWidgetStyle });

// 监听 activeWidget 变化，同步样式表单
watch(
  () => activeWidget.value?.style,
  (style) => {
    styleForm.value = { ...defaultWidgetStyle, ...style };
  },
  { immediate: true },
);

// 更新样式配置
const updateStyle = (key: keyof WidgetStyle, value: any) => {
  if (!activeWidget.value) return;
  styleForm.value[key] = value;
  store.updateWidgetStyle(activeWidget.value.id, { [key]: value });
};

// 边框样式选项
const borderStyleOptions = [
  { label: $t('dashboard-design.attribute.borderStyle.solid'), value: 'solid' },
  { label: $t('dashboard-design.attribute.borderStyle.dashed'), value: 'dashed' },
  { label: $t('dashboard-design.attribute.borderStyle.dotted'), value: 'dotted' },
  { label: $t('dashboard-design.attribute.borderStyle.none'), value: 'none' },
];

// 折线图/柱状图系列数据操作
const updateSeriesName = (index: number, name: string) => {
  if (!activeWidget.value) return;
  const seriesData = [...(formData.value.seriesData || [])];
  if (seriesData[index]) {
    seriesData[index] = { ...seriesData[index], name };
    updateProps('seriesData', seriesData);
  }
};

const updateSeriesData = (index: number, val: string) => {
  if (!activeWidget.value) return;
  const seriesData = [...(formData.value.seriesData || [])];
  if (seriesData[index]) {
    const data = val
      .split(',')
      .map((s) => {
        const num = Number(s.trim());
        return isNaN(num) ? 0 : num;
      })
      .filter((_, i, arr) => i < arr.length || arr[i] !== 0);
    seriesData[index] = { ...seriesData[index], data };
    updateProps('seriesData', seriesData);
  }
};

const addSeries = () => {
  if (!activeWidget.value) return;
  const seriesData = [...(formData.value.seriesData || [])];
  const xAxisData = formData.value.xAxisData || [];
  const newName = `${$t('dashboard-design.attribute.chart.seriesNamePrefix')}${seriesData.length + 1}`;
  const newData = Array.from({ length: xAxisData.length }).fill(0);
  seriesData.push({
    name: newName,
    data: newData,
  });
  updateProps('seriesData', seriesData);
  // 更新本地状态
  localSeriesNames.value.push(newName);
  localSeriesData.value.push(newData.join(', '));
};

const removeSeries = (index: number) => {
  if (!activeWidget.value) return;
  const seriesData = [...(formData.value.seriesData || [])];
  seriesData.splice(index, 1);
  updateProps('seriesData', seriesData);
  // 更新本地状态
  localSeriesNames.value.splice(index, 1);
  localSeriesData.value.splice(index, 1);
};

// 饼图数据操作
const updatePieItem = (
  index: number,
  key: 'name' | 'value',
  val: number | string,
) => {
  if (!activeWidget.value) return;
  const seriesData = [...(formData.value.seriesData || [])];
  if (seriesData[index]) {
    seriesData[index] = { ...seriesData[index], [key]: val };
    updateProps('seriesData', seriesData);
  }
};

const addPieItem = () => {
  if (!activeWidget.value) return;
  const seriesData = [...(formData.value.seriesData || [])];
  seriesData.push({ name: `${$t('dashboard-design.attribute.chart.itemNamePrefix')}${seriesData.length + 1}`, value: 100 });
  updateProps('seriesData', seriesData);
};

const removePieItem = (index: number) => {
  if (!activeWidget.value) return;
  const seriesData = [...(formData.value.seriesData || [])];
  seriesData.splice(index, 1);
  updateProps('seriesData', seriesData);
};

// 通用列表数据操作
const updateListItem = (
  listKey: string,
  index: number,
  key: string,
  val: any,
) => {
  if (!activeWidget.value) return;
  const list = [...(formData.value[listKey] || [])];
  if (list[index]) {
    list[index] = { ...list[index], [key]: val };
    updateProps(listKey, list);
  }
};

const removeListItem = (listKey: string, index: number) => {
  if (!activeWidget.value) return;
  const list = [...(formData.value[listKey] || [])];
  list.splice(index, 1);
  updateProps(listKey, list);
};

// 待办列表操作
const addTodoItem = () => {
  if (!activeWidget.value) return;
  const items = [...(formData.value.items || [])];
  items.push({
    id: String(Date.now()),
    title: $t('dashboard-design.attribute.widget.todo.newItem'),
    done: false,
    priority: 'medium',
  });
  updateProps('items', items);
};

// 排行榜操作
const updateRankingItem = (index: number, key: string, val: any) => {
  if (!activeWidget.value) return;
  const items = [...(formData.value.items || [])];
  if (items[index]) {
    items[index] = { ...items[index], [key]: val, rank: index + 1 };
    updateProps('items', items);
  }
};

const addRankingItem = () => {
  if (!activeWidget.value) return;
  const items = [...(formData.value.items || [])];
  items.push({ rank: items.length + 1, name: $t('dashboard-design.attribute.widget.ranking.newItem'), value: 0 });
  updateProps('items', items);
};

// 快捷入口菜单选择
const menuSelectorRef = ref<InstanceType<typeof ZqMenuSelector> | null>(null);
const currentEditingCellIndex = ref<number>(-1);

// 获取指定索引的菜单
const getMenuAtIndex = (index: number) => {
  const menus = formData.value.menus || [];
  return menus[index] || null;
};

// 打开菜单选择弹窗
const openMenuSelectorForCell = (index: number) => {
  currentEditingCellIndex.value = index;
  menuSelectorRef.value?.open();
};

// 选择菜单回调
const handleMenuSelect = (menu: MenuItem) => {
  if (!activeWidget.value || currentEditingCellIndex.value < 0) return;

  const totalCells = (formData.value.columns || 4) * (formData.value.rows || 2);
  const menus = [...(formData.value.menus || [])];

  // 确保数组长度足够
  while (menus.length < totalCells) {
    menus.push(null);
  }

  // 设置指定位置的菜单
  menus[currentEditingCellIndex.value] = {
    id: menu.id,
    title: menu.title || menu.name,
    icon: menu.icon,
    path: menu.path,
  };

  updateProps('menus', menus);
  currentEditingCellIndex.value = -1;
};

// 删除指定索引的菜单
const removeMenuAtIndex = (index: number) => {
  if (!activeWidget.value) return;
  const menus = [...(formData.value.menus || [])];
  if (menus[index]) {
    menus[index] = null;
    updateProps('menus', menus);
  }
};

// 图片轮播操作
const updateImageItem = (index: number, key: string, val: any) => {
  if (!activeWidget.value) return;
  const images = [...(formData.value.images || [])];
  if (images[index]) {
    images[index] = { ...images[index], [key]: val };
    updateProps('images', images);
  }
};

const addImageItem = () => {
  if (!activeWidget.value) return;
  const images = [...(formData.value.images || [])];
  images.push({ url: '', title: $t('dashboard-design.attribute.widget.carousel.newItem'), link: '' });
  updateProps('images', images);
};

// 图片组件预览列表操作
const updatePreviewImage = (index: number, val: string) => {
  if (!activeWidget.value) return;
  const list = [...(formData.value.previewSrcList || [])];
  if (list[index] !== undefined) {
    list[index] = val;
    updateProps('previewSrcList', list);
  }
};

const addPreviewImage = () => {
  if (!activeWidget.value) return;
  const list = [...(formData.value.previewSrcList || [])];
  list.push('');
  updateProps('previewSrcList', list);
};

const removePreviewImage = (index: number) => {
  if (!activeWidget.value) return;
  const list = [...(formData.value.previewSrcList || [])];
  list.splice(index, 1);
  updateProps('previewSrcList', list);
};

// 轮播图图片选择处理 - 保存文件ID，使用 file:// 前缀标识
const handleCarouselImageSelect = async (
  fileIds: string | string[] | undefined,
) => {
  if (!activeWidget.value || !fileIds) return;
  const ids = Array.isArray(fileIds) ? fileIds : [fileIds];
  const images = [...(formData.value.images || [])];

  for (const id of ids) {
    // 使用 file:// 前缀标识这是文件ID，渲染时动态转换
    images.push({ url: `file://${id}`, title: $t('dashboard-design.attribute.widget.carousel.newItem'), link: '' });
  }
  updateProps('images', images);
};

// 图片组件主图选择处理 - 保存文件ID
const handleImageSelect = async (fileId: string | string[] | undefined) => {
  if (!activeWidget.value || !fileId) return;
  const id = Array.isArray(fileId) ? fileId[0] : fileId;
  if (id) {
    updateProps('src', `file://${id}`);
  }
};

// 图片组件预览列表选择处理 - 保存文件ID
const handlePreviewImageSelect = async (
  fileIds: string | string[] | undefined,
) => {
  if (!activeWidget.value || !fileIds) return;
  const ids = Array.isArray(fileIds) ? fileIds : [fileIds];
  const list = [...(formData.value.previewSrcList || [])];

  for (const id of ids) {
    list.push(`file://${id}`);
  }
  updateProps('previewSrcList', list);
};

// 视频选择处理 - 保存文件ID
const handleVideoSelect = async (fileId: string | string[] | undefined) => {
  if (!activeWidget.value || !fileId) return;
  const id = Array.isArray(fileId) ? fileId[0] : fileId;
  if (id) {
    updateProps('url', `file://${id}`);
  }
};

// 静态数据编辑模式
const staticDataEditMode = ref<'form' | 'json'>('form');

// 本地编辑状态（用于避免输入时光标跳动）
const localXAxisData = ref('');
const localJsonData = ref('');
const localSeriesNames = ref<string[]>([]);
const localSeriesData = ref<string[]>([]);

// 初始化本地编辑状态
const initLocalEditState = () => {
  if (!activeWidget.value) return;
  localXAxisData.value = (formData.value.xAxisData || []).join(', ');
  localSeriesNames.value = (formData.value.seriesData || []).map(
    (s: any) => s.name || '',
  );
  localSeriesData.value = (formData.value.seriesData || []).map((s: any) =>
    (s.data || []).join(', '),
  );
};

// 监听 widget 变化，重新初始化本地状态
watch(
  () => activeWidget.value?.id,
  () => {
    initLocalEditState();
    // 重置 JSON 编辑状态
    localJsonData.value = '';
  },
  { immediate: true },
);

// 监听编辑模式切换
watch(staticDataEditMode, (mode) => {
  if (mode === 'json') {
    localJsonData.value = staticDataJson.value;
  } else {
    initLocalEditState();
  }
});

// 获取静态数据 JSON
const staticDataJson = computed(() => {
  if (!activeWidget.value) return '';
  const type = activeWidget.value.type;

  switch (type) {
    case 'chart-area':
    case 'chart-bar':
    case 'chart-line': {
      return JSON.stringify(
        {
          xAxisData: formData.value.xAxisData || [],
          seriesData: formData.value.seriesData || [],
        },
        null,
        2,
      );
    }
    case 'chart-funnel':
    case 'chart-pie': {
      return JSON.stringify(
        {
          seriesData: formData.value.seriesData || [],
        },
        null,
        2,
      );
    }
    case 'chart-gauge': {
      return JSON.stringify(
        {
          value: formData.value.value || 0,
        },
        null,
        2,
      );
    }
    case 'chart-heatmap': {
      return JSON.stringify(
        {
          xAxisData: formData.value.xAxisData || [],
          yAxisData: formData.value.yAxisData || [],
          seriesData: formData.value.seriesData || [],
        },
        null,
        2,
      );
    }
    case 'chart-kline': {
      return JSON.stringify(
        {
          xAxisData: formData.value.xAxisData || [],
          seriesData: formData.value.seriesData || [],
        },
        null,
        2,
      );
    }
    case 'chart-radar': {
      return JSON.stringify(
        {
          indicators: formData.value.indicators || [],
          seriesData: formData.value.seriesData || [],
        },
        null,
        2,
      );
    }
    case 'chart-ring': {
      return JSON.stringify(
        {
          seriesData: formData.value.seriesData || [],
        },
        null,
        2,
      );
    }
    case 'chart-sankey': {
      return JSON.stringify(
        {
          nodes: formData.value.nodes || [],
          links: formData.value.links || [],
        },
        null,
        2,
      );
    }
    case 'chart-scatter': {
      return JSON.stringify(
        {
          seriesData: formData.value.seriesData || [],
        },
        null,
        2,
      );
    }
    // No default
  }
  return '{}';
});

// 更新静态数据 JSON
const updateStaticDataJson = (jsonStr: string) => {
  if (!activeWidget.value) return;
  try {
    const data = JSON.parse(jsonStr);
    const type = activeWidget.value.type;

    switch (type) {
      case 'chart-area':
      case 'chart-bar':
      case 'chart-line': {
        if (data.xAxisData) updateProps('xAxisData', data.xAxisData);
        if (data.seriesData) updateProps('seriesData', data.seriesData);

        break;
      }
      case 'chart-funnel':
      case 'chart-pie': {
        if (data.seriesData) updateProps('seriesData', data.seriesData);

        break;
      }
      case 'chart-gauge': {
        if (data.value !== undefined) updateProps('value', data.value);

        break;
      }
      case 'chart-heatmap': {
        if (data.xAxisData) updateProps('xAxisData', data.xAxisData);
        if (data.yAxisData) updateProps('yAxisData', data.yAxisData);
        if (data.seriesData) updateProps('seriesData', data.seriesData);

        break;
      }
      case 'chart-kline': {
        if (data.xAxisData) updateProps('xAxisData', data.xAxisData);
        if (data.seriesData) updateProps('seriesData', data.seriesData);

        break;
      }
      case 'chart-radar': {
        if (data.indicators) updateProps('indicators', data.indicators);
        if (data.seriesData) updateProps('seriesData', data.seriesData);

        break;
      }
      case 'chart-ring': {
        if (data.seriesData) updateProps('seriesData', data.seriesData);

        break;
      }
      case 'chart-sankey': {
        if (data.nodes) updateProps('nodes', data.nodes);
        if (data.links) updateProps('links', data.links);

        break;
      }
      case 'chart-scatter': {
        if (data.seriesData) updateProps('seriesData', data.seriesData);

        break;
      }
      // No default
    }
  } catch {
    // JSON 解析失败，忽略
  }
};
</script>

<template>
  <div
    class="attribute-panel flex h-full"
    :class="isPanelCollapsed ? 'w-14' : 'w-80'"
  >
    <!-- 左侧内容区域 -->
    <div v-if="!isPanelCollapsed" class="flex flex-1 flex-col overflow-hidden">
      <!-- 未选中组件时显示仪表盘全局设置 -->
      <ElScrollbar v-if="!activeWidget" class="flex-1">
        <div class="p-4">
          <div class="text-muted-foreground mb-4 text-sm">{{ $t('dashboard-design.attribute.globalSettings') }}</div>
          <ElForm label-position="top" size="small">
            <ElFormItem :label="$t('dashboard-design.attribute.dashboardName')">
              <ElInput
                v-model="store.dashboardConfig.name"
                :placeholder="$t('dashboard-design.attribute.placeholder.name')"
                @change="
                  (val: string) => store.updateDashboardConfig({ name: val })
                "
              />
            </ElFormItem>

            <ElDivider content-position="left">{{ $t('dashboard-design.attribute.gridLayout') }}</ElDivider>
            <ElFormItem :label="$t('dashboard-design.attribute.columns')">
              <ElInputNumber
                v-model="store.dashboardConfig.columns"
                :min="6"
                :max="24"
                controls-position="right"
                class="w-full"
                @change="
                  (val: number | undefined) =>
                    store.updateDashboardConfig({ columns: val || 12 })
                "
              />
            </ElFormItem>
            <ElFormItem :label="$t('dashboard-design.attribute.rowHeight')">
              <ElInputNumber
                v-model="store.dashboardConfig.rowHeight"
                :min="20"
                :max="100"
                controls-position="right"
                class="w-full"
                @change="
                  (val: number | undefined) =>
                    store.updateDashboardConfig({ rowHeight: val || 50 })
                "
              />
            </ElFormItem>
            <ElFormItem :label="$t('dashboard-design.attribute.widgetMargin')">
              <div class="flex gap-2">
                <ElInputNumber
                  :model-value="store.dashboardConfig.margin[0]"
                  :min="0"
                  :max="30"
                  controls-position="right"
                  class="flex-1"
                  :placeholder="$t('dashboard-design.attribute.horizontal')"
                  @change="
                    (val: number | undefined) =>
                      store.updateDashboardConfig({
                        margin: [val || 0, store.dashboardConfig.margin[1]],
                      })
                  "
                />
                <ElInputNumber
                  :model-value="store.dashboardConfig.margin[1]"
                  :min="0"
                  :max="30"
                  controls-position="right"
                  class="flex-1"
                  :placeholder="$t('dashboard-design.attribute.vertical')"
                  @change="
                    (val: number | undefined) =>
                      store.updateDashboardConfig({
                        margin: [store.dashboardConfig.margin[0], val || 0],
                      })
                  "
                />
              </div>
              <div class="text-muted-foreground mt-1 text-xs">{{ $t('dashboard-design.attribute.horizontal') }} / {{ $t('dashboard-design.attribute.vertical') }}</div>
            </ElFormItem>

            <ElDivider content-position="left">{{ $t('dashboard-design.attribute.background') }}</ElDivider>
            <ElFormItem :label="$t('dashboard-design.attribute.backgroundColor')">
              <div class="flex w-full items-center gap-2">
                <ElColorPicker
                  v-model="store.dashboardConfig.backgroundColor"
                  @change="
                    (val: string | null) =>
                      store.updateDashboardConfig({
                        backgroundColor: val || '',
                      })
                  "
                />
                <span class="text-muted-foreground flex-1 text-xs">{{
                  store.dashboardConfig.backgroundColor || $t('dashboard-design.attribute.colorTheme.default')
                }}</span>
                <ElButton
                  v-if="store.dashboardConfig.backgroundColor"
                  size="small"
                  text
                  @click="store.updateDashboardConfig({ backgroundColor: '' })"
                >
                  {{ $t('dashboard-design.attribute.reset') }}
                </ElButton>
              </div>
            </ElFormItem>

            <ElDivider content-position="left">{{ $t('dashboard-design.attribute.display') }}</ElDivider>
            <ElFormItem :label="$t('dashboard-design.attribute.outerMargin')">
              <ElSwitch
                v-model="store.dashboardConfig.showOuterMargin"
                @change="
                  (val: string | number | boolean) =>
                    store.updateDashboardConfig({ showOuterMargin: !!val })
                "
              />
              <span class="text-muted-foreground ml-2 text-xs"
                >{{ $t('dashboard-design.attribute.outerMarginTip') }}</span
              >
            </ElFormItem>
          </ElForm>
        </div>
      </ElScrollbar>
      <!-- 选中组件时显示配置 -->
      <ElScrollbar v-else class="flex-1">
        <div class="p-4">
          <ElForm label-position="top" size="small">
            <!-- 基础配置 -->
            <template v-if="activeTab === 'basic'">
              <ElFormItem :label="$t('dashboard-design.attribute.title')">
                <ElInput
                  v-model="formData.title"
                  :placeholder="$t('dashboard-design.attribute.placeholder.title')"
                  @change="updateTitle"
                />
              </ElFormItem>

              <!-- 布局信息 -->
              <ElDivider content-position="left">{{ $t('dashboard-design.attribute.layout') }}</ElDivider>
              <ElFormItem :label="$t('dashboard-design.attribute.widthGrid')">
                <ElInputNumber
                  :model-value="activeWidget.w"
                  :min="activeWidget.minW || 1"
                  :max="12"
                  controls-position="right"
                  class="w-full"
                  disabled
                />
              </ElFormItem>
              <ElFormItem :label="$t('dashboard-design.attribute.heightGrid')">
                <ElInputNumber
                  :model-value="activeWidget.h"
                  :min="activeWidget.minH || 1"
                  controls-position="right"
                  class="w-full"
                  disabled
                />
              </ElFormItem>
              <div class="text-muted-foreground mb-2 text-xs">
                {{ $t('dashboard-design.attribute.layoutTip') }}
              </div>

              <!-- 统计卡片配置 -->
              <template v-if="activeWidget.type === 'stat-card'">
                <ElDivider content-position="left">{{ $t('dashboard-design.attribute.iconConfig') }}</ElDivider>
                <ElFormItem :label="$t('dashboard-design.attribute.icon')">
                  <ElSelect
                    v-model="formData.iconName"
                    class="w-full"
                    @change="(val: string) => updateProps('iconName', val)"
                  >
                    <ElOption
                      v-for="opt in iconOptions"
                      :key="opt.value"
                      :label="opt.label"
                      :value="opt.value"
                    />
                  </ElSelect>
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.iconColor')">
                  <ElColorPicker
                    v-model="formData.iconColor"
                    @change="
                      (val: string | null) => updateProps('iconColor', val)
                    "
                  />
                </ElFormItem>
              </template>

              <!-- 进度卡片配置 -->
              <template v-if="activeWidget.type === 'progress-card'">
                <ElDivider content-position="left">{{ $t('dashboard-design.attribute.styleConfig') }}</ElDivider>
                <ElFormItem :label="$t('dashboard-design.attribute.status')">
                  <ElSelect
                    v-model="formData.status"
                    class="w-full"
                    @change="(val: string) => updateProps('status', val)"
                  >
                    <ElOption
                      v-for="opt in progressStatusOptions"
                      :key="opt.value"
                      :label="opt.label"
                      :value="opt.value"
                    />
                  </ElSelect>
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.strokeWidth')">
                  <ElInputNumber
                    v-model="formData.strokeWidth"
                    :min="1"
                    :max="30"
                    controls-position="right"
                    class="w-full"
                    @change="
                      (val: number | undefined) =>
                        updateProps('strokeWidth', val)
                    "
                  />
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.display')">
                  <ElSwitch
                    v-model="formData.showText"
                    @change="
                      (val: string | number | boolean) =>
                        updateProps('showText', val)
                    "
                  />
                </ElFormItem>
              </template>

              <!-- 折线图配置 -->
              <template v-if="activeWidget.type === 'chart-line'">
                <ElDivider content-position="left">{{ $t('dashboard-design.attribute.styleConfig') }}</ElDivider>
                <ElFormItem :label="$t('dashboard-design.attribute.colorTheme.label') || '颜色主题'">
                  <ElSelect
                    :model-value="formData.colorTheme || 'default'"
                    class="w-full"
                    @change="
                      (val: string) => {
                        const theme = colorThemeOptions.find(
                          (t) => t.value === val,
                        );
                        if (theme) {
                          updateProps('colors', theme.colors);
                          updateProps('colorTheme', val);
                        }
                      }
                    "
                  >
                    <ElOption
                      v-for="opt in colorThemeOptions"
                      :key="opt.value"
                      :label="opt.label"
                      :value="opt.value"
                    />
                  </ElSelect>
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.chart.smooth')">
                  <ElSwitch
                    v-model="formData.smooth"
                    @change="
                      (val: string | number | boolean) =>
                        updateProps('smooth', val)
                    "
                  />
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.chart.showArea')">
                  <ElSwitch
                    v-model="formData.showArea"
                    @change="
                      (val: string | number | boolean) =>
                        updateProps('showArea', val)
                    "
                  />
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.chart.showSymbol')">
                  <ElSwitch
                    v-model="formData.showSymbol"
                    @change="
                      (val: string | number | boolean) =>
                        updateProps('showSymbol', val)
                    "
                  />
                </ElFormItem>
                <ElFormItem v-if="formData.showSymbol" :label="$t('dashboard-design.attribute.chart.symbolSize')">
                  <ElInputNumber
                    v-model="formData.symbolSize"
                    :min="2"
                    :max="20"
                    controls-position="right"
                    class="w-full"
                    @change="
                      (val: number | undefined) =>
                        updateProps('symbolSize', val)
                    "
                  />
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.strokeWidth')">
                  <ElInputNumber
                    v-model="formData.lineWidth"
                    :min="1"
                    :max="10"
                    controls-position="right"
                    class="w-full"
                    @change="
                      (val: number | undefined) => updateProps('lineWidth', val)
                    "
                  />
                </ElFormItem>
                <ElDivider content-position="left">{{ $t('dashboard-design.attribute.chart.axis') }}</ElDivider>
                <ElFormItem :label="$t('dashboard-design.attribute.chart.xAxisName')">
                  <ElInput
                    v-model="formData.xAxisName"
                    :placeholder="$t('dashboard-design.attribute.chart.placeholder.xAxis')"
                    @change="(val: string) => updateProps('xAxisName', val)"
                  />
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.chart.yAxisName')">
                  <ElInput
                    v-model="formData.yAxisName"
                    :placeholder="$t('dashboard-design.attribute.chart.placeholder.yAxis')"
                    @change="(val: string) => updateProps('yAxisName', val)"
                  />
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.chart.nameLocation')">
                  <ElSelect
                    v-model="formData.axisNameLocation"
                    class="w-full"
                    @change="
                      (val: string) => updateProps('axisNameLocation', val)
                    "
                  >
                    <ElOption :label="$t('dashboard-design.attribute.chart.location.start')" value="start" />
                    <ElOption :label="$t('dashboard-design.attribute.chart.location.middle')" value="middle" />
                    <ElOption :label="$t('dashboard-design.attribute.chart.location.end')" value="end" />
                  </ElSelect>
                </ElFormItem>
                <ElDivider content-position="left">{{ $t('dashboard-design.attribute.chart.legend') }}</ElDivider>
                <ElFormItem :label="$t('dashboard-design.attribute.chart.showLegend')">
                  <ElSwitch
                    v-model="formData.showLegend"
                    @change="
                      (val: string | number | boolean) =>
                        updateProps('showLegend', val)
                    "
                  />
                </ElFormItem>
                <ElFormItem v-if="formData.showLegend" :label="$t('dashboard-design.attribute.chart.legendPosition')">
                  <ElSelect
                    v-model="formData.legendPosition"
                    class="w-full"
                    @change="
                      (val: string) => updateProps('legendPosition', val)
                    "
                  >
                    <ElOption :label="$t('dashboard-design.attribute.chart.location.top')" value="top" />
                    <ElOption :label="$t('dashboard-design.attribute.chart.location.bottom')" value="bottom" />
                    <ElOption :label="$t('dashboard-design.attribute.chart.location.left')" value="left" />
                    <ElOption :label="$t('dashboard-design.attribute.chart.location.right')" value="right" />
                  </ElSelect>
                </ElFormItem>
              </template>

              <!-- 柱状图配置 -->
              <template v-if="activeWidget.type === 'chart-bar'">
                <ElDivider content-position="left">{{ $t('dashboard-design.attribute.styleConfig') }}</ElDivider>
                <ElFormItem :label="$t('dashboard-design.attribute.colorTheme.label') || '颜色主题'">
                  <ElSelect
                    :model-value="formData.colorTheme || 'default'"
                    class="w-full"
                    @change="
                      (val: string) => {
                        const theme = colorThemeOptions.find(
                          (t) => t.value === val,
                        );
                        if (theme) {
                          updateProps('colors', theme.colors);
                          updateProps('colorTheme', val);
                        }
                      }
                    "
                  >
                    <ElOption
                      v-for="opt in colorThemeOptions"
                      :key="opt.value"
                      :label="opt.label"
                      :value="opt.value"
                    />
                  </ElSelect>
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.chart.horizontal')">
                  <ElSwitch
                    v-model="formData.horizontal"
                    @change="
                      (val: string | number | boolean) =>
                        updateProps('horizontal', val)
                    "
                  />
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.chart.stack')">
                  <ElSwitch
                    v-model="formData.stack"
                    @change="
                      (val: string | number | boolean) =>
                        updateProps('stack', val)
                    "
                  />
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.chart.showBackground')">
                  <ElSwitch
                    v-model="formData.showBackground"
                    @change="
                      (val: string | number | boolean) =>
                        updateProps('showBackground', val)
                    "
                  />
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.chart.barWidth')">
                  <ElSelect
                    :model-value="formData.barWidth || 'auto'"
                    class="w-full"
                    @change="(val: string) => updateProps('barWidth', val)"
                  >
                    <ElOption :label="$t('dashboard-design.attribute.chart.barWidthOptions.auto')" value="auto" />
                    <ElOption :label="$t('dashboard-design.attribute.chart.barWidthOptions.thin')" value="30%" />
                    <ElOption :label="$t('dashboard-design.attribute.chart.barWidthOptions.medium')" value="50%" />
                    <ElOption :label="$t('dashboard-design.attribute.chart.barWidthOptions.thick')" value="70%" />
                  </ElSelect>
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.chart.barRadius')">
                  <ElInputNumber
                    v-model="formData.barRadius"
                    :min="0"
                    :max="20"
                    controls-position="right"
                    class="w-full"
                    @change="
                      (val: number | undefined) => updateProps('barRadius', val)
                    "
                  />
                </ElFormItem>
                <ElDivider content-position="left">{{ $t('dashboard-design.attribute.chart.axis') }}</ElDivider>
                <ElFormItem :label="$t('dashboard-design.attribute.chart.xAxisName')">
                  <ElInput
                    v-model="formData.xAxisName"
                    :placeholder="$t('dashboard-design.attribute.chart.placeholder.xAxis')"
                    @change="(val: string) => updateProps('xAxisName', val)"
                  />
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.chart.yAxisName')">
                  <ElInput
                    v-model="formData.yAxisName"
                    :placeholder="$t('dashboard-design.attribute.chart.placeholder.yAxis')"
                    @change="(val: string) => updateProps('yAxisName', val)"
                  />
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.chart.nameLocation')">
                  <ElSelect
                    v-model="formData.axisNameLocation"
                    class="w-full"
                    @change="
                      (val: string) => updateProps('axisNameLocation', val)
                    "
                  >
                    <ElOption :label="$t('dashboard-design.attribute.chart.location.start')" value="start" />
                    <ElOption :label="$t('dashboard-design.attribute.chart.location.middle')" value="middle" />
                    <ElOption :label="$t('dashboard-design.attribute.chart.location.end')" value="end" />
                  </ElSelect>
                </ElFormItem>
                <ElDivider content-position="left">{{ $t('dashboard-design.attribute.chart.legend') }}</ElDivider>
                <ElFormItem :label="$t('dashboard-design.attribute.chart.showLegend')">
                  <ElSwitch
                    v-model="formData.showLegend"
                    @change="
                      (val: string | number | boolean) =>
                        updateProps('showLegend', val)
                    "
                  />
                </ElFormItem>
                <ElFormItem v-if="formData.showLegend" :label="$t('dashboard-design.attribute.chart.legendPosition')">
                  <ElSelect
                    v-model="formData.legendPosition"
                    class="w-full"
                    @change="
                      (val: string) => updateProps('legendPosition', val)
                    "
                  >
                    <ElOption :label="$t('dashboard-design.attribute.chart.location.top')" value="top" />
                    <ElOption :label="$t('dashboard-design.attribute.chart.location.bottom')" value="bottom" />
                    <ElOption :label="$t('dashboard-design.attribute.chart.location.left')" value="left" />
                    <ElOption :label="$t('dashboard-design.attribute.chart.location.right')" value="right" />
                  </ElSelect>
                </ElFormItem>
              </template>

              <!-- 饼图配置 -->
              <template v-if="activeWidget.type === 'chart-pie'">
                <ElDivider content-position="left">{{ $t('dashboard-design.attribute.styleConfig') }}</ElDivider>
                <ElFormItem :label="$t('dashboard-design.attribute.colorTheme.label') || '颜色主题'">
                  <ElSelect
                    :model-value="formData.colorTheme || 'default'"
                    class="w-full"
                    @change="
                      (val: string) => {
                        const theme = colorThemeOptions.find(
                          (t) => t.value === val,
                        );
                        if (theme) {
                          updateProps('colors', theme.colors);
                          updateProps('colorTheme', val);
                        }
                      }
                    "
                  >
                    <ElOption
                      v-for="opt in colorThemeOptions"
                      :key="opt.value"
                      :label="opt.label"
                      :value="opt.value"
                    />
                  </ElSelect>
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.chart.pieType')">
                  <ElSelect
                    v-model="formData.pieType"
                    class="w-full"
                    @change="(val: string) => updateProps('pieType', val)"
                  >
                    <ElOption :label="$t('dashboard-design.attribute.chart.pieTypes.pie')" value="pie" />
                    <ElOption :label="$t('dashboard-design.attribute.chart.pieTypes.ring')" value="ring" />
                    <ElOption :label="$t('dashboard-design.attribute.chart.pieTypes.rose')" value="rose" />
                  </ElSelect>
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.chart.showLabel')">
                  <ElSwitch
                    v-model="formData.showLabel"
                    @change="
                      (val: string | number | boolean) =>
                        updateProps('showLabel', val)
                    "
                  />
                </ElFormItem>
                <ElFormItem v-if="formData.showLabel" :label="$t('dashboard-design.attribute.chart.labelPosition')">
                  <ElSelect
                    v-model="formData.labelPosition"
                    class="w-full"
                    @change="(val: string) => updateProps('labelPosition', val)"
                  >
                    <ElOption :label="$t('dashboard-design.attribute.chart.labelPositions.outside')" value="outside" />
                    <ElOption :label="$t('dashboard-design.attribute.chart.labelPositions.inside')" value="inside" />
                  </ElSelect>
                </ElFormItem>
                <ElDivider content-position="left">{{ $t('dashboard-design.attribute.chart.legend') }}</ElDivider>
                <ElFormItem :label="$t('dashboard-design.attribute.chart.showLegend')">
                  <ElSwitch
                    v-model="formData.showLegend"
                    @change="
                      (val: string | number | boolean) =>
                        updateProps('showLegend', val)
                    "
                  />
                </ElFormItem>
                <ElFormItem v-if="formData.showLegend" :label="$t('dashboard-design.attribute.chart.legendPosition')">
                  <ElSelect
                    v-model="formData.legendPosition"
                    class="w-full"
                    @change="
                      (val: string) => updateProps('legendPosition', val)
                    "
                  >
                    <ElOption :label="$t('dashboard-design.attribute.chart.location.top')" value="top" />
                    <ElOption :label="$t('dashboard-design.attribute.chart.location.bottom')" value="bottom" />
                    <ElOption :label="$t('dashboard-design.attribute.chart.location.left')" value="left" />
                    <ElOption :label="$t('dashboard-design.attribute.chart.location.right')" value="right" />
                  </ElSelect>
                </ElFormItem>
              </template>

              <!-- 仪表盘配置 -->
              <template v-if="activeWidget.type === 'chart-gauge'">
                <ElDivider content-position="left">{{ $t('dashboard-design.attribute.chart.numerical') }}</ElDivider>
                <ElFormItem :label="$t('dashboard-design.attribute.chart.currentValue')">
                  <ElInputNumber
                    v-model="formData.value"
                    :min="formData.min || 0"
                    :max="formData.max || 100"
                    :step="0.1"
                    controls-position="right"
                    class="w-full"
                    @change="
                      (val: number | undefined) => updateProps('value', val)
                    "
                  />
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.chart.min')">
                  <ElInputNumber
                    v-model="formData.min"
                    controls-position="right"
                    class="w-full"
                    @change="
                      (val: number | undefined) => updateProps('min', val)
                    "
                  />
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.chart.max')">
                  <ElInputNumber
                    v-model="formData.max"
                    controls-position="right"
                    class="w-full"
                    @change="
                      (val: number | undefined) => updateProps('max', val)
                    "
                  />
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.chart.unit')">
                  <ElInput
                    v-model="formData.unit"
                    :placeholder="$t('dashboard-design.attribute.chart.placeholder.unit')"
                    @change="(val: string) => updateProps('unit', val)"
                  />
                </ElFormItem>
                <ElDivider content-position="left">{{ $t('dashboard-design.attribute.styleConfig') }}</ElDivider>
                <ElFormItem :label="$t('dashboard-design.attribute.chart.splitNumber')">
                  <ElInputNumber
                    v-model="formData.splitNumber"
                    :min="2"
                    :max="20"
                    controls-position="right"
                    class="w-full"
                    @change="
                      (val: number | undefined) =>
                        updateProps('splitNumber', val)
                    "
                  />
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.chart.showProgress')">
                  <ElSwitch
                    v-model="formData.showProgress"
                    @change="
                      (val: string | number | boolean) =>
                        updateProps('showProgress', val)
                    "
                  />
                </ElFormItem>
              </template>

              <!-- 面积图配置 -->
              <template v-if="activeWidget.type === 'chart-area'">
                <ElDivider content-position="left">{{ $t('dashboard-design.attribute.styleConfig') }}</ElDivider>
                <ElFormItem :label="$t('dashboard-design.attribute.colorTheme.label') || '颜色主题'">
                  <ElSelect
                    :model-value="formData.colorTheme || 'default'"
                    class="w-full"
                    @change="
                      (val: string) => {
                        const theme = colorThemeOptions.find(
                          (t) => t.value === val,
                        );
                        if (theme) {
                          updateProps('colors', theme.colors);
                          updateProps('colorTheme', val);
                        }
                      }
                    "
                  >
                    <ElOption
                      v-for="opt in colorThemeOptions"
                      :key="opt.value"
                      :label="opt.label"
                      :value="opt.value"
                    />
                  </ElSelect>
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.chart.smooth')">
                  <ElSwitch
                    v-model="formData.smooth"
                    @change="
                      (val: string | number | boolean) =>
                        updateProps('smooth', val)
                    "
                  />
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.chart.stack')">
                  <ElSwitch
                    v-model="formData.stack"
                    @change="
                      (val: string | number | boolean) =>
                        updateProps('stack', val)
                    "
                  />
                </ElFormItem>
                <ElDivider content-position="left">{{ $t('dashboard-design.attribute.chart.axis') }}</ElDivider>
                <ElFormItem :label="$t('dashboard-design.attribute.chart.xAxisName')">
                  <ElInput
                    v-model="formData.xAxisName"
                    :placeholder="$t('dashboard-design.attribute.chart.placeholder.xAxis')"
                    @change="(val: string) => updateProps('xAxisName', val)"
                  />
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.chart.yAxisName')">
                  <ElInput
                    v-model="formData.yAxisName"
                    :placeholder="$t('dashboard-design.attribute.chart.placeholder.yAxis')"
                    @change="(val: string) => updateProps('yAxisName', val)"
                  />
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.chart.nameLocation')">
                  <ElSelect
                    v-model="formData.axisNameLocation"
                    class="w-full"
                    @change="
                      (val: string) => updateProps('axisNameLocation', val)
                    "
                  >
                    <ElOption :label="$t('dashboard-design.attribute.chart.location.start')" value="start" />
                    <ElOption :label="$t('dashboard-design.attribute.chart.location.middle')" value="middle" />
                    <ElOption :label="$t('dashboard-design.attribute.chart.location.end')" value="end" />
                  </ElSelect>
                </ElFormItem>
                <ElDivider content-position="left">{{ $t('dashboard-design.attribute.chart.legend') }}</ElDivider>
                <ElFormItem :label="$t('dashboard-design.attribute.chart.showLegend')">
                  <ElSwitch
                    v-model="formData.showLegend"
                    @change="
                      (val: string | number | boolean) =>
                        updateProps('showLegend', val)
                    "
                  />
                </ElFormItem>
                <ElFormItem v-if="formData.showLegend" :label="$t('dashboard-design.attribute.chart.legendPosition')">
                  <ElSelect
                    v-model="formData.legendPosition"
                    class="w-full"
                    @change="
                      (val: string) => updateProps('legendPosition', val)
                    "
                  >
                    <ElOption :label="$t('dashboard-design.attribute.chart.location.top')" value="top" />
                    <ElOption :label="$t('dashboard-design.attribute.chart.location.bottom')" value="bottom" />
                    <ElOption :label="$t('dashboard-design.attribute.chart.location.left')" value="left" />
                    <ElOption :label="$t('dashboard-design.attribute.chart.location.right')" value="right" />
                  </ElSelect>
                </ElFormItem>
              </template>

              <!-- 雷达图配置 -->
              <template v-if="activeWidget.type === 'chart-radar'">
                <ElDivider content-position="left">{{ $t('dashboard-design.attribute.styleConfig') }}</ElDivider>
                <ElFormItem :label="$t('dashboard-design.attribute.colorTheme.label') || '颜色主题'">
                  <ElSelect
                    :model-value="formData.colorTheme || 'default'"
                    class="w-full"
                    @change="
                      (val: string) => {
                        const theme = colorThemeOptions.find(
                          (t) => t.value === val,
                        );
                        if (theme) {
                          updateProps('colors', theme.colors);
                          updateProps('colorTheme', val);
                        }
                      }
                    "
                  >
                    <ElOption
                      v-for="opt in colorThemeOptions"
                      :key="opt.value"
                      :label="opt.label"
                      :value="opt.value"
                    />
                  </ElSelect>
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.chart.shape')">
                  <ElSelect
                    v-model="formData.shape"
                    class="w-full"
                    @change="(val: string) => updateProps('shape', val)"
                  >
                    <ElOption :label="$t('dashboard-design.attribute.chart.shapes.polygon')" value="polygon" />
                    <ElOption :label="$t('dashboard-design.attribute.chart.shapes.circle')" value="circle" />
                  </ElSelect>
                </ElFormItem>
                <ElDivider content-position="left">{{ $t('dashboard-design.attribute.chart.legend') }}</ElDivider>
                <ElFormItem :label="$t('dashboard-design.attribute.chart.showLegend')">
                  <ElSwitch
                    v-model="formData.showLegend"
                    @change="
                      (val: string | number | boolean) =>
                        updateProps('showLegend', val)
                    "
                  />
                </ElFormItem>
                <ElFormItem v-if="formData.showLegend" :label="$t('dashboard-design.attribute.chart.legendPosition')">
                  <ElSelect
                    v-model="formData.legendPosition"
                    class="w-full"
                    @change="
                      (val: string) => updateProps('legendPosition', val)
                    "
                  >
                    <ElOption :label="$t('dashboard-design.attribute.chart.location.top')" value="top" />
                    <ElOption :label="$t('dashboard-design.attribute.chart.location.bottom')" value="bottom" />
                    <ElOption :label="$t('dashboard-design.attribute.chart.location.left')" value="left" />
                    <ElOption :label="$t('dashboard-design.attribute.chart.location.right')" value="right" />
                  </ElSelect>
                </ElFormItem>
              </template>

              <!-- 漏斗图配置 -->
              <template v-if="activeWidget.type === 'chart-funnel'">
                <ElDivider content-position="left">{{ $t('dashboard-design.attribute.styleConfig') }}</ElDivider>
                <ElFormItem :label="$t('dashboard-design.attribute.colorTheme.label')">
                  <ElSelect
                    :model-value="formData.colorTheme || 'default'"
                    class="w-full"
                    @change="
                      (val: string) => {
                        const theme = colorThemeOptions.find(
                          (t) => t.value === val,
                        );
                        if (theme) {
                          updateProps('colors', theme.colors);
                          updateProps('colorTheme', val);
                        }
                      }
                    "
                  >
                    <ElOption
                      v-for="opt in colorThemeOptions"
                      :key="opt.value"
                      :label="opt.label"
                      :value="opt.value"
                    />
                  </ElSelect>
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.chart.sort')">
                  <ElSelect
                    v-model="formData.sort"
                    class="w-full"
                    @change="(val: string) => updateProps('sort', val)"
                  >
                    <ElOption :label="$t('dashboard-design.chart.sortOptions.descending')" value="descending" />
                    <ElOption :label="$t('dashboard-design.chart.sortOptions.ascending')" value="ascending" />
                    <ElOption :label="$t('dashboard-design.chart.sortOptions.none')" value="none" />
                  </ElSelect>
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.chart.orient')">
                  <ElSelect
                    v-model="formData.orient"
                    class="w-full"
                    @change="(val: string) => updateProps('orient', val)"
                  >
                    <ElOption :label="$t('dashboard-design.chart.orientOptions.vertical')" value="vertical" />
                    <ElOption :label="$t('dashboard-design.chart.orientOptions.horizontal')" value="horizontal" />
                  </ElSelect>
                </ElFormItem>
                <ElDivider content-position="left">{{ $t('dashboard-design.chart.legend') }}</ElDivider>
                <ElFormItem :label="$t('dashboard-design.chart.showLegend')">
                  <ElSwitch
                    v-model="formData.showLegend"
                    @change="
                      (val: string | number | boolean) =>
                        updateProps('showLegend', val)
                    "
                  />
                </ElFormItem>
                <ElFormItem v-if="formData.showLegend" :label="$t('dashboard-design.chart.legendPosition')">
                  <ElSelect
                    v-model="formData.legendPosition"
                    class="w-full"
                    @change="
                      (val: string) => updateProps('legendPosition', val)
                    "
                  >
                    <ElOption :label="$t('dashboard-design.chart.location.top')" value="top" />
                    <ElOption :label="$t('dashboard-design.chart.location.bottom')" value="bottom" />
                    <ElOption :label="$t('dashboard-design.chart.location.left')" value="left" />
                    <ElOption :label="$t('dashboard-design.chart.location.right')" value="right" />
                  </ElSelect>
                </ElFormItem>
              </template>

              <!-- 散点图配置 -->
              <template v-if="activeWidget.type === 'chart-scatter'">
                <ElDivider content-position="left">{{ $t('dashboard-design.attribute.styleConfig') }}</ElDivider>
                <ElFormItem :label="$t('dashboard-design.attribute.colorTheme.label') || '颜色主题'">
                  <ElSelect
                    :model-value="formData.colorTheme || 'default'"
                    class="w-full"
                    @change="
                      (val: string) => {
                        const theme = colorThemeOptions.find(
                          (t) => t.value === val,
                        );
                        if (theme) {
                          updateProps('colors', theme.colors);
                          updateProps('colorTheme', val);
                        }
                      }
                    "
                  >
                    <ElOption
                      v-for="opt in colorThemeOptions"
                      :key="opt.value"
                      :label="opt.label"
                      :value="opt.value"
                    />
                  </ElSelect>
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.chart.pointSize')">
                  <ElInputNumber
                    v-model="formData.symbolSize"
                    :min="4"
                    :max="30"
                    controls-position="right"
                    class="w-full"
                    @change="
                      (val: number | undefined) =>
                        updateProps('symbolSize', val)
                    "
                  />
                </ElFormItem>
                <ElDivider content-position="left">{{ $t('dashboard-design.attribute.chart.axis') }}</ElDivider>
                <ElFormItem :label="$t('dashboard-design.attribute.chart.xAxisName')">
                  <ElInput
                    v-model="formData.xAxisName"
                    :placeholder="$t('dashboard-design.attribute.chart.placeholder.xAxis')"
                    @change="(val: string) => updateProps('xAxisName', val)"
                  />
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.chart.yAxisName')">
                  <ElInput
                    v-model="formData.yAxisName"
                    :placeholder="$t('dashboard-design.attribute.chart.placeholder.yAxis')"
                    @change="(val: string) => updateProps('yAxisName', val)"
                  />
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.chart.nameLocation')">
                  <ElSelect
                    v-model="formData.axisNameLocation"
                    class="w-full"
                    @change="
                      (val: string) => updateProps('axisNameLocation', val)
                    "
                  >
                    <ElOption :label="$t('dashboard-design.attribute.chart.location.start')" value="start" />
                    <ElOption :label="$t('dashboard-design.attribute.chart.location.middle')" value="middle" />
                    <ElOption :label="$t('dashboard-design.attribute.chart.location.end')" value="end" />
                  </ElSelect>
                </ElFormItem>
                <ElDivider content-position="left">{{ $t('dashboard-design.attribute.chart.legend') }}</ElDivider>
                <ElFormItem :label="$t('dashboard-design.attribute.chart.showLegend')">
                  <ElSwitch
                    v-model="formData.showLegend"
                    @change="
                      (val: string | number | boolean) =>
                        updateProps('showLegend', val)
                    "
                  />
                </ElFormItem>
                <ElFormItem v-if="formData.showLegend" :label="$t('dashboard-design.attribute.chart.legendPosition')">
                  <ElSelect
                    v-model="formData.legendPosition"
                    class="w-full"
                    @change="
                      (val: string) => updateProps('legendPosition', val)
                    "
                  >
                    <ElOption :label="$t('dashboard-design.attribute.chart.location.top')" value="top" />
                    <ElOption :label="$t('dashboard-design.attribute.chart.location.bottom')" value="bottom" />
                    <ElOption :label="$t('dashboard-design.attribute.chart.location.left')" value="left" />
                    <ElOption :label="$t('dashboard-design.attribute.chart.location.right')" value="right" />
                  </ElSelect>
                </ElFormItem>
              </template>

              <!-- 环形进度图配置 -->
              <template v-if="activeWidget.type === 'chart-ring'">
                <ElDivider content-position="left">{{ $t('dashboard-design.attribute.styleConfig') }}</ElDivider>
                <ElFormItem :label="$t('dashboard-design.attribute.colorTheme.label') || '颜色主题'">
                  <ElSelect
                    :model-value="formData.colorTheme || 'default'"
                    class="w-full"
                    @change="
                      (val: string) => {
                        const theme = colorThemeOptions.find(
                          (t) => t.value === val,
                        );
                        if (theme) {
                          updateProps('colors', theme.colors);
                          updateProps('colorTheme', val);
                        }
                      }
                    "
                  >
                    <ElOption
                      v-for="opt in colorThemeOptions"
                      :key="opt.value"
                      :label="opt.label"
                      :value="opt.value"
                    />
                  </ElSelect>
                </ElFormItem>
              </template>

              <!-- 热力图配置 -->
              <template v-if="activeWidget.type === 'chart-heatmap'">
                <ElDivider content-position="left">{{ $t('dashboard-design.attribute.chart.numerical') }}</ElDivider>
                <ElFormItem :label="$t('dashboard-design.attribute.chart.min')">
                  <ElInputNumber
                    v-model="formData.minValue"
                    controls-position="right"
                    class="w-full"
                    @change="
                      (val: number | undefined) => updateProps('minValue', val)
                    "
                  />
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.chart.max')">
                  <ElInputNumber
                    v-model="formData.maxValue"
                    controls-position="right"
                    class="w-full"
                    @change="
                      (val: number | undefined) => updateProps('maxValue', val)
                    "
                  />
                </ElFormItem>
              </template>

              <!-- K线图配置 -->
              <template v-if="activeWidget.type === 'chart-kline'">
                <ElDivider content-position="left">{{ $t('dashboard-design.attribute.chart.maConfig') }}</ElDivider>
                <ElFormItem :label="$t('dashboard-design.attribute.chart.showMA5')">
                  <ElSwitch
                    v-model="formData.showMA5"
                    @change="
                      (val: string | number | boolean) =>
                        updateProps('showMA5', val)
                    "
                  />
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.chart.showMA10')">
                  <ElSwitch
                    v-model="formData.showMA10"
                    @change="
                      (val: string | number | boolean) =>
                        updateProps('showMA10', val)
                    "
                  />
                </ElFormItem>
              </template>

              <!-- 桑基图配置 -->
              <template v-if="activeWidget.type === 'chart-sankey'">
                <ElDivider content-position="left">{{ $t('dashboard-design.attribute.styleConfig') }}</ElDivider>
                <ElFormItem :label="$t('dashboard-design.attribute.colorTheme.label') || '颜色主题'">
                  <ElSelect
                    :model-value="formData.colorTheme || 'default'"
                    class="w-full"
                    @change="
                      (val: string) => {
                        const theme = colorThemeOptions.find(
                          (t) => t.value === val,
                        );
                        if (theme) {
                          updateProps('colors', theme.colors);
                          updateProps('colorTheme', val);
                        }
                      }
                    "
                  >
                    <ElOption
                      v-for="opt in colorThemeOptions"
                      :key="opt.value"
                      :label="opt.label"
                      :value="opt.value"
                    />
                  </ElSelect>
                </ElFormItem>
              </template>

              <!-- 快捷入口配置 -->
              <template v-if="activeWidget.type === 'quick-links'">
                <ElFormItem :label="$t('dashboard-design.attribute.columns')">
                  <ElInputNumber
                    v-model="formData.columns"
                    :min="2"
                    :max="8"
                    controls-position="right"
                    class="w-full"
                    @change="
                      (val: number | undefined) =>
                        updateProps('columns', val || 4)
                    "
                  />
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.vertical')">
                  <ElInputNumber
                    v-model="formData.rows"
                    :min="1"
                    :max="6"
                    controls-position="right"
                    class="w-full"
                    @change="
                      (val: number | undefined) => updateProps('rows', val || 2)
                    "
                  />
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.iconColor')">
                  <div class="flex w-full items-center gap-2">
                    <ElColorPicker
                      v-model="formData.iconColor"
                      @change="
                        (val: string | null) =>
                          updateProps('iconColor', val || '')
                      "
                    />
                    <span class="text-muted-foreground flex-1 text-xs">{{
                      formData.iconColor || $t('dashboard-design.attribute.widget.quickLinks.iconColorDefault')
                    }}</span>
                    <ElButton
                      v-if="formData.iconColor"
                      size="small"
                      text
                      @click="updateProps('iconColor', '')"
                    >
                      {{ $t('dashboard-design.attribute.reset') }}
                    </ElButton>
                  </div>
                </ElFormItem>
              </template>

              <!-- 欢迎卡片配置 -->
              <template v-if="activeWidget.type === 'welcome-card'">
                <ElFormItem :label="$t('dashboard-design.attribute.widget.welcome.subtitle')">
                  <ElInput
                    v-model="formData.subtitle"
                    :placeholder="$t('dashboard-design.attribute.widget.welcome.subtitlePlaceholder')"
                    @change="(val: string) => updateProps('subtitle', val)"
                  />
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.widget.welcome.showTime')">
                  <ElSwitch
                    v-model="formData.showTime"
                    @change="
                      (val: string | number | boolean) =>
                        updateProps('showTime', val)
                    "
                  />
                </ElFormItem>
              </template>

              <!-- 倒计时配置 -->
              <template v-if="activeWidget.type === 'countdown'">
                <ElDivider content-position="left">{{ $t('dashboard-design.attribute.widget.countdown.config') }}</ElDivider>
                <ElFormItem :label="$t('dashboard-design.attribute.widget.countdown.targetTime')">
                  <ElDatePicker
                    v-model="formData.targetTime"
                    type="datetime"
                    :placeholder="$t('dashboard-design.attribute.widget.countdown.targetTimePlaceholder')"
                    class="w-full"
                    @change="
                      (val: any) =>
                        updateProps(
                          'targetTime',
                          val ? new Date(val).toISOString() : '',
                        )
                    "
                  />
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.widget.countdown.showDays')">
                  <ElSwitch
                    v-model="formData.showDays"
                    @change="
                      (val: string | number | boolean) =>
                        updateProps('showDays', val)
                    "
                  />
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.widget.countdown.showHours')">
                  <ElSwitch
                    v-model="formData.showHours"
                    @change="
                      (val: string | number | boolean) =>
                        updateProps('showHours', val)
                    "
                  />
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.widget.countdown.showMinutes')">
                  <ElSwitch
                    v-model="formData.showMinutes"
                    @change="
                      (val: string | number | boolean) =>
                        updateProps('showMinutes', val)
                    "
                  />
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.widget.countdown.showSeconds')">
                  <ElSwitch
                    v-model="formData.showSeconds"
                    @change="
                      (val: string | number | boolean) =>
                        updateProps('showSeconds', val)
                    "
                  />
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.widget.countdown.finishedText')">
                  <ElInput
                    v-model="formData.finishedText"
                    :placeholder="$t('dashboard-design.attribute.widget.countdown.finishedTextPlaceholder')"
                    @change="(val: string) => updateProps('finishedText', val)"
                  />
                </ElFormItem>
              </template>

              <!-- 时钟配置 -->
              <template v-if="activeWidget.type === 'clock'">
                <ElDivider content-position="left">{{ $t('dashboard-design.attribute.widget.clock.config') }}</ElDivider>
                <ElFormItem :label="$t('dashboard-design.attribute.widget.clock.showDate')">
                  <ElSwitch
                    v-model="formData.showDate"
                    @change="
                      (val: string | number | boolean) =>
                        updateProps('showDate', val)
                    "
                  />
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.widget.clock.showSeconds')">
                  <ElSwitch
                    v-model="formData.showSeconds"
                    @change="
                      (val: string | number | boolean) =>
                        updateProps('showSeconds', val)
                    "
                  />
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.widget.clock.format24')">
                  <ElSwitch
                    v-model="formData.format24"
                    @change="
                      (val: string | number | boolean) =>
                        updateProps('format24', val)
                    "
                  />
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.widget.clock.timezone')">
                  <ElSelect
                    v-model="formData.timezone"
                    class="w-full"
                    @change="(val: string) => updateProps('timezone', val)"
                  >
                    <ElOption :label="$t('dashboard-design.attribute.widget.clock.timezoneOptions.local')" value="local" />
                    <ElOption label="UTC" value="UTC" />
                    <ElOption :label="$t('dashboard-design.attribute.widget.clock.timezoneOptions.beijing')" value="Asia/Shanghai" />
                    <ElOption :label="$t('dashboard-design.attribute.widget.clock.timezoneOptions.tokyo')" value="Asia/Tokyo" />
                    <ElOption :label="$t('dashboard-design.attribute.widget.clock.timezoneOptions.newyork')" value="America/New_York" />
                    <ElOption :label="$t('dashboard-design.attribute.widget.clock.timezoneOptions.london')" value="Europe/London" />
                  </ElSelect>
                </ElFormItem>
              </template>

              <!-- 天气配置 -->
              <template v-if="activeWidget.type === 'weather'">
                <ElDivider content-position="left">{{ $t('dashboard-design.attribute.widget.weather.config') }}</ElDivider>
                <ElFormItem :label="$t('dashboard-design.attribute.widgets.weather.city')">
                  <ElInput
                    v-model="formData.city"
                    :placeholder="$t('dashboard-design.attribute.widget.weather.cityPlaceholder')"
                    @change="(val: string) => updateProps('city', val)"
                  />
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.widget.weather.temp')">
                  <ElInputNumber
                    v-model="formData.temperature"
                    controls-position="right"
                    class="w-full"
                    @change="
                      (val: number | undefined) =>
                        updateProps('temperature', val)
                    "
                  />
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.widget.weather.weather')">
                  <ElInput
                    v-model="formData.weather"
                    :placeholder="$t('dashboard-design.attribute.widget.weather.weatherPlaceholder')"
                    @change="(val: string) => updateProps('weather', val)"
                  />
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.widget.weather.icon')">
                  <ElSelect
                    v-model="formData.icon"
                    class="w-full"
                    @change="(val: string) => updateProps('icon', val)"
                  >
                    <ElOption :label="$t('dashboard-design.attribute.widget.weather.icons.sunny')" value="sunny" />
                    <ElOption :label="$t('dashboard-design.attribute.widget.weather.icons.cloudy')" value="cloudy" />
                    <ElOption :label="$t('dashboard-design.attribute.widget.weather.icons.partlyCloudy')" value="partly-cloudy" />
                    <ElOption :label="$t('dashboard-design.attribute.widget.weather.icons.rainy')" value="rainy" />
                    <ElOption :label="$t('dashboard-design.attribute.widget.weather.icons.snowy')" value="snowy" />
                    <ElOption :label="$t('dashboard-design.attribute.widget.weather.icons.foggy')" value="foggy" />
                  </ElSelect>
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.widget.weather.humidity')">
                  <ElInputNumber
                    v-model="formData.humidity"
                    :min="0"
                    :max="100"
                    controls-position="right"
                    class="w-full"
                    @change="
                      (val: number | undefined) => updateProps('humidity', val)
                    "
                  />
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.widgets.weather.wind')">
                  <ElInput
                    v-model="formData.wind"
                    :placeholder="$t('dashboard-design.attribute.widget.weather.windPlaceholder')"
                    @change="(val: string) => updateProps('wind', val)"
                  />
                </ElFormItem>
              </template>

              <!-- 图片轮播配置 -->
              <template v-if="activeWidget.type === 'image-carousel'">
                <ElDivider content-position="left">{{ $t('dashboard-design.attribute.widget.carousel.config') }}</ElDivider>
                <ElFormItem :label="$t('dashboard-design.attribute.widget.carousel.autoplay')">
                  <ElSwitch
                    v-model="formData.autoplay"
                    @change="
                      (val: string | number | boolean) =>
                        updateProps('autoplay', val)
                    "
                  />
                </ElFormItem>
                <ElFormItem v-if="formData.autoplay" :label="$t('dashboard-design.attribute.widget.carousel.interval')">
                  <ElInputNumber
                    v-model="formData.interval"
                    :min="1000"
                    :max="10000"
                    :step="500"
                    controls-position="right"
                    class="w-full"
                    @change="
                      (val: number | undefined) => updateProps('interval', val)
                    "
                  />
                  <div class="text-muted-foreground mt-1 text-xs">{{ $t('dashboard-design.attribute.widget.carousel.intervalUnit') }}</div>
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.widget.carousel.showIndicator')">
                  <ElSwitch
                    v-model="formData.showIndicator"
                    @change="
                      (val: string | number | boolean) =>
                        updateProps('showIndicator', val)
                    "
                  />
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.widget.carousel.showArrow')">
                  <ElSwitch
                    v-model="formData.showArrow"
                    @change="
                      (val: string | number | boolean) =>
                        updateProps('showArrow', val)
                    "
                  />
                </ElFormItem>
              </template>

              <!-- 数据表格配置 -->
              <template v-if="activeWidget.type === 'data-table'">
                <ElDivider content-position="left">{{ $t('dashboard-design.attribute.widget.table.config') }}</ElDivider>
                <ElFormItem :label="$t('dashboard-design.attribute.widget.table.stripe')">
                  <ElSwitch
                    v-model="formData.stripe"
                    @change="
                      (val: string | number | boolean) =>
                        updateProps('stripe', val)
                    "
                  />
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.borderStyle.none')">
                  <ElSwitch
                    v-model="formData.border"
                    @change="
                      (val: string | number | boolean) =>
                        updateProps('border', val)
                    "
                  />
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.widget.table.showIndex')">
                  <ElSwitch
                    v-model="formData.showIndex"
                    @change="
                      (val: string | number | boolean) =>
                        updateProps('showIndex', val)
                    "
                  />
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.status')">
                  <ElSelect
                    v-model="formData.size"
                    class="w-full"
                    @change="(val: string) => updateProps('size', val)"
                  >
                    <ElOption :label="$t('dashboard-design.attribute.widget.table.sizeOptions.default')" value="default" />
                    <ElOption :label="$t('dashboard-design.attribute.widget.table.sizeOptions.large')" value="large" />
                    <ElOption :label="$t('dashboard-design.attribute.widget.table.sizeOptions.small')" value="small" />
                  </ElSelect>
                </ElFormItem>
              </template>

              <!-- iframe 配置 -->
              <template v-if="activeWidget.type === 'iframe'">
                <ElDivider content-position="left">{{ $t('dashboard-design.attribute.widget.iframe.config') }}</ElDivider>
                <ElFormItem :label="$t('dashboard-design.attribute.widget.iframe.showBorder')">
                  <ElSwitch
                    v-model="formData.showBorder"
                    @change="
                      (val: string | number | boolean) =>
                        updateProps('showBorder', val)
                    "
                  />
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.widget.iframe.allowFullscreen')">
                  <ElSwitch
                    v-model="formData.allowFullscreen"
                    @change="
                      (val: string | number | boolean) =>
                        updateProps('allowFullscreen', val)
                    "
                  />
                </ElFormItem>
              </template>

              <!-- 视频播放器配置 -->
              <template v-if="activeWidget.type === 'video-player'">
                <ElDivider content-position="left">{{ $t('dashboard-design.attribute.widget.video.config') }}</ElDivider>
                <ElFormItem :label="$t('dashboard-design.attribute.widget.carousel.autoplay')">
                  <ElSwitch
                    v-model="formData.autoplay"
                    @change="
                      (val: string | number | boolean) =>
                        updateProps('autoplay', val)
                    "
                  />
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.widget.video.loop')">
                  <ElSwitch
                    v-model="formData.loop"
                    @change="
                      (val: string | number | boolean) =>
                        updateProps('loop', val)
                    "
                  />
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.widget.video.muted')">
                  <ElSwitch
                    v-model="formData.muted"
                    @change="
                      (val: string | number | boolean) =>
                        updateProps('muted', val)
                    "
                  />
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.widget.video.controls')">
                  <ElSwitch
                    v-model="formData.controls"
                    @change="
                      (val: string | number | boolean) =>
                        updateProps('controls', val)
                    "
                  />
                </ElFormItem>
              </template>

              <!-- 图片组件配置 -->
              <template v-if="activeWidget.type === 'image'">
                <ElDivider content-position="left">{{ $t('dashboard-design.attribute.widget.image.config') }}</ElDivider>
                <ElFormItem :label="$t('dashboard-design.attribute.widget.image.alt')">
                  <ElInput
                    v-model="formData.alt"
                    :placeholder="$t('dashboard-design.attribute.widget.image.altPlaceholder')"
                    @change="(val: string) => updateProps('alt', val)"
                  />
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.widget.image.fit')">
                  <ElSelect
                    v-model="formData.fit"
                    class="w-full"
                    @change="(val: string) => updateProps('fit', val)"
                  >
                    <ElOption :label="$t('dashboard-design.attribute.widget.image.fitOptions.cover')" value="cover" />
                    <ElOption :label="$t('dashboard-design.attribute.widget.image.fitOptions.contain')" value="contain" />
                    <ElOption :label="$t('dashboard-design.attribute.widget.image.fitOptions.fill')" value="fill" />
                    <ElOption :label="$t('dashboard-design.attribute.widget.image.fitOptions.none')" value="none" />
                    <ElOption :label="$t('dashboard-design.attribute.widget.image.fitOptions.scaleDown')" value="scale-down" />
                  </ElSelect>
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.widget.image.lazy')">
                  <ElSwitch
                    v-model="formData.lazy"
                    @change="
                      (val: string | number | boolean) =>
                        updateProps('lazy', val)
                    "
                  />
                </ElFormItem>
                <ElDivider content-position="left">{{ $t('dashboard-design.attribute.widget.image.previewConfig') }}</ElDivider>
                <ElFormItem :label="$t('dashboard-design.attribute.widget.image.zIndex')">
                  <ElInputNumber
                    v-model="formData.zIndex"
                    :min="1"
                    :max="9999"
                    controls-position="right"
                    class="w-full"
                    @change="
                      (val: number | undefined) => updateProps('zIndex', val)
                    "
                  />
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.widget.image.closeOnClickModal')">
                  <ElSwitch
                    v-model="formData.hideOnClickModal"
                    @change="
                      (val: string | number | boolean) =>
                        updateProps('hideOnClickModal', val)
                    "
                  />
                </ElFormItem>
              </template>
            </template>

            <!-- 数据源配置 -->
            <template v-if="activeTab === 'dataSource'">
              <!-- 图片轮播和图片组件：静态数据 / 图片上传 -->
              <template
                v-if="
                  activeWidget.type === 'image-carousel' ||
                  activeWidget.type === 'image'
                "
              >
                <ElFormItem :label="$t('dashboard-design.attribute.dataSource.dataType')">
                  <ElRadioGroup
                    v-model="dataSourceForm.type"
                    size="small"
                    @change="updateDataSource"
                  >
                    <ElRadioButton value="static">{{ $t('dashboard-design.attribute.dataSource.static') }}</ElRadioButton>
                    <ElRadioButton value="upload">{{ $t('dashboard-design.attribute.dataSource.uploadImage') }}</ElRadioButton>
                  </ElRadioGroup>
                </ElFormItem>
              </template>

              <!-- 视频播放器：静态数据 / 视频上传 -->
              <template v-else-if="activeWidget.type === 'video-player'">
                <ElFormItem :label="$t('dashboard-design.attribute.dataSource.dataType')">
                  <ElRadioGroup
                    v-model="dataSourceForm.type"
                    size="small"
                    @change="updateDataSource"
                  >
                    <ElRadioButton value="static">{{ $t('dashboard-design.attribute.dataSource.static') }}</ElRadioButton>
                    <ElRadioButton value="upload">{{ $t('dashboard-design.attribute.dataSource.uploadVideo') }}</ElRadioButton>
                  </ElRadioGroup>
                </ElFormItem>
              </template>

              <!-- 其他组件：静态数据 / 数据源 / API接口 -->
              <template v-else>
                <ElFormItem :label="$t('dashboard-design.attribute.dataSource.dataType')">
                  <ElRadioGroup
                    v-model="dataSourceForm.type"
                    size="small"
                    @change="
                      (val: any) => {
                        updateDataSource();
                        if (val === 'dataSource') loadDataSourceList();
                      }
                    "
                  >
                    <ElRadioButton value="static">{{ $t('dashboard-design.attribute.dataSource.static') }}</ElRadioButton>
                    <ElRadioButton value="dataSource">{{ $t('dashboard-design.attribute.dataSource.dataSource') }}</ElRadioButton>
                    <ElRadioButton value="api">{{ $t('dashboard-design.attribute.dataSource.api') }}</ElRadioButton>
                  </ElRadioGroup>
                </ElFormItem>
              </template>

              <!-- 数据源配置 -->
              <template v-if="dataSourceForm.type === 'dataSource'">
                <ElDivider content-position="left">{{ $t('dashboard-design.attribute.dataSource.config') }}</ElDivider>

                <ElFormItem :label="$t('dashboard-design.attribute.dataSource.select')">
                  <ElSelect
                    v-model="dataSourceForm.dataSourceCode"
                    :placeholder="$t('dashboard-design.attribute.dataSource.selectPlaceholder')"
                    filterable
                    :loading="loadingDataSource"
                    class="w-full"
                    @change="updateDataSource"
                    @focus="loadDataSourceList"
                  >
                    <ElOption
                      v-for="ds in dataSourceList"
                      :key="ds.code"
                      :label="ds.name"
                      :value="ds.code"
                    >
                      <div class="flex w-full items-center justify-between">
                        <span>{{ ds.name }}</span>
                        <div class="ml-2 flex items-center gap-1">
                          <ElTag
                            v-if="ds.result_type"
                            size="small"
                            type="primary"
                          >
                            {{ getResultTypeLabel(ds.result_type) }}
                          </ElTag>
                          <span class="text-xs text-gray-400">{{
                            ds.code
                          }}</span>
                        </div>
                      </div>
                    </ElOption>
                  </ElSelect>
                </ElFormItem>

                <ElDivider content-position="left">{{ $t('dashboard-design.attribute.dataSource.mapping') }}</ElDivider>

                <div class="mb-2">
                  <div
                    v-for="(mapping, index) in dataSourceForm.fieldMappings"
                    :key="index"
                    class="mb-2 flex items-center gap-2"
                  >
                    <ElInput
                      :model-value="mapping.source"
                      :placeholder="$t('dashboard-design.attribute.dataSource.sourceField')"
                      size="small"
                      class="flex-1"
                      @change="
                        (val: string) =>
                          updateFieldMapping(index, 'source', val)
                      "
                    />
                    <span class="text-muted-foreground">→</span>
                    <ElSelect
                      :model-value="mapping.target"
                      :placeholder="$t('dashboard-design.attribute.dataSource.targetField')"
                      size="small"
                      class="flex-1"
                      @change="
                        (val: string) =>
                          updateFieldMapping(index, 'target', val)
                      "
                    >
                      <ElOption
                        v-for="field in fieldTargets"
                        :key="field.key"
                        :label="field.label"
                        :value="field.key"
                      />
                    </ElSelect>
                    <ElButton
                      type="danger"
                      size="small"
                      circle
                      @click="removeFieldMapping(index)"
                    >
                      <Trash2 class="h-3 w-3" />
                    </ElButton>
                  </div>
                  <ElButton
                    type="primary"
                    size="small"
                    plain
                    @click="addFieldMapping"
                  >
                    <Plus class="mr-1 h-3 w-3" />
                    {{ $t('dashboard-design.attribute.dataSource.addMapping') }}
                  </ElButton>
                </div>

                <div
                  class="text-muted-foreground mt-2 rounded bg-gray-50 p-2 text-xs dark:bg-gray-800"
                >
                  <p>{{ $t('dashboard-design.attribute.dataSource.mappingTip') }}</p>
                </div>

                <ElDivider content-position="left">{{ $t('dashboard-design.attribute.dataSource.refresh') }}</ElDivider>

                <ElFormItem :label="$t('dashboard-design.attribute.dataSource.autoRefresh')">
                  <ElSwitch
                    v-model="dataSourceForm.refreshEnabled"
                    @change="updateDataSource"
                  />
                </ElFormItem>

                <ElFormItem
                  v-if="dataSourceForm.refreshEnabled"
                  :label="$t('dashboard-design.attribute.dataSource.interval')"
                >
                  <ElInputNumber
                    v-model="dataSourceForm.refreshInterval"
                    :min="5"
                    :max="3600"
                    :step="5"
                    controls-position="right"
                    class="w-full"
                    @change="updateDataSource"
                  />
                  <div class="text-muted-foreground mt-1 text-xs">
                    {{ $t('dashboard-design.attribute.dataSource.intervalUnit') }}
                  </div>
                </ElFormItem>
              </template>

              <template v-if="dataSourceForm.type === 'api'">
                <ElDivider content-position="left">{{ $t('dashboard-design.attribute.dataSource.apiConfig') }}</ElDivider>

                <ElFormItem :label="$t('dashboard-design.attribute.dataSource.apiUrl')">
                  <ElInput
                    v-model="dataSourceForm.apiUrl"
                    :placeholder="$t('dashboard-design.attribute.dataSource.apiUrlPlaceholder')"
                    @change="updateDataSource"
                  />
                </ElFormItem>

                <ElFormItem :label="$t('dashboard-design.attribute.dataSource.apiMethod')">
                  <ElSelect
                    v-model="dataSourceForm.apiMethod"
                    class="w-full"
                    @change="updateDataSource"
                  >
                    <ElOption label="GET" value="GET" />
                    <ElOption label="POST" value="POST" />
                  </ElSelect>
                </ElFormItem>

                <ElFormItem :label="$t('dashboard-design.attribute.dataSource.dataPath')">
                  <ElInput
                    v-model="dataSourceForm.dataPath"
                    :placeholder="$t('dashboard-design.attribute.dataSource.dataPathPlaceholder')"
                    @change="updateDataSource"
                  />
                  <div class="text-muted-foreground mt-1 text-xs">
                    {{ $t('dashboard-design.attribute.dataSource.dataPathTip') }}
                  </div>
                </ElFormItem>

                <ElDivider content-position="left">{{ $t('dashboard-design.attribute.dataSource.mapping') }}</ElDivider>

                <div class="mb-2">
                  <div
                    v-for="(mapping, index) in dataSourceForm.fieldMappings"
                    :key="index"
                    class="mb-2 flex items-center gap-2"
                  >
                    <ElInput
                      :model-value="mapping.source"
                      :placeholder="$t('dashboard-design.attribute.dataSource.sourceField')"
                      size="small"
                      class="flex-1"
                      @change="
                        (val: string) =>
                          updateFieldMapping(index, 'source', val)
                      "
                    />
                    <span class="text-muted-foreground">→</span>
                    <ElSelect
                      :model-value="mapping.target"
                      :placeholder="$t('dashboard-design.attribute.dataSource.targetField')"
                      size="small"
                      class="flex-1"
                      @change="
                        (val: string) =>
                          updateFieldMapping(index, 'target', val)
                      "
                    >
                      <ElOption
                        v-for="field in fieldTargets"
                        :key="field.key"
                        :label="field.label"
                        :value="field.key"
                      />
                    </ElSelect>
                    <ElButton
                      size="small"
                      type="danger"
                      text
                      @click="removeFieldMapping(index)"
                    >
                      <Trash2 class="h-3.5 w-3.5" />
                    </ElButton>
                  </div>
                  <ElButton
                    size="small"
                    type="primary"
                    text
                    class="w-full"
                    @click="addFieldMapping"
                  >
                    <Plus class="mr-1 h-3.5 w-3.5" />
                    {{ $t('dashboard-design.attribute.dataSource.addMapping') }}
                  </ElButton>
                </div>

                <ElDivider content-position="left">{{ $t('dashboard-design.attribute.dataSource.autoRefresh') }}</ElDivider>

                <ElFormItem :label="$t('dashboard-design.attribute.dataSource.enableRefresh')">
                  <ElSwitch
                    v-model="dataSourceForm.refreshEnabled"
                    @change="updateDataSource"
                  />
                </ElFormItem>

                <ElFormItem
                  v-if="dataSourceForm.refreshEnabled"
                  :label="$t('dashboard-design.attribute.dataSource.intervalSeconds')"
                >
                  <ElInputNumber
                    v-model="dataSourceForm.refreshInterval"
                    :min="5"
                    :max="3600"
                    :step="5"
                    controls-position="right"
                    class="w-full"
                    @change="updateDataSource"
                  />
                </ElFormItem>
              </template>

              <!-- 静态数据编辑 -->
              <template v-if="dataSourceForm.type === 'static'">
                <!-- 图表类型才显示编辑模式切换 -->
                <template
                  v-if="
                    [
                      'chart-line',
                      'chart-bar',
                      'chart-pie',
                      'chart-gauge',
                      'chart-area',
                      'chart-radar',
                      'chart-funnel',
                      'chart-scatter',
                      'chart-ring',
                      'chart-heatmap',
                      'chart-kline',
                      'chart-sankey',
                    ].includes(activeWidget.type)
                  "
                >
                  <div class="mb-3 flex items-center justify-between">
                    <span class="text-muted-foreground text-xs">{{ $t('dashboard-design.attribute.chart.dataEditMode') }}</span>
                    <ElRadioGroup v-model="staticDataEditMode" size="small">
                      <ElRadioButton value="form">{{ $t('dashboard-design.attribute.chart.dataEditForm') }}</ElRadioButton>
                      <ElRadioButton value="json">{{ $t('dashboard-design.attribute.chart.dataEditJson') }}</ElRadioButton>
                    </ElRadioGroup>
                  </div>

                  <!-- JSON 编辑模式 -->
                  <template v-if="staticDataEditMode === 'json'">
                    <ElInput
                      type="textarea"
                      :rows="12"
                      v-model="localJsonData"
                      :placeholder="$t('dashboard-design.attribute.chart.jsonPlaceholder')"
                      class="font-mono text-xs"
                      @blur="updateStaticDataJson(localJsonData)"
                    />
                    <div class="text-muted-foreground mt-2 text-xs">
                      {{ $t('dashboard-design.attribute.chart.jsonTip') }}
                    </div>
                  </template>

                  <!-- 表单编辑模式 -->
                  <template v-else>
                    <!-- 折线图/柱状图/面积图静态数据 -->
                    <template
                      v-if="
                        activeWidget.type === 'chart-line' ||
                        activeWidget.type === 'chart-bar' ||
                        activeWidget.type === 'chart-area'
                      "
                    >
                      <ElDivider content-position="left">{{ $t('dashboard-design.attribute.chart.xAxisData') }}</ElDivider>
                      <ElFormItem>
                        <ElInput
                          type="textarea"
                          :rows="2"
                          v-model="localXAxisData"
                          :placeholder="$t('dashboard-design.attribute.chart.placeholder.xAxis2')"
                          @blur="
                            updateProps(
                              'xAxisData',
                              localXAxisData
                                .split(',')
                                .map((s) => s.trim())
                                .filter(Boolean),
                            )
                          "
                        />
                      </ElFormItem>

                      <ElDivider content-position="left">{{ $t('dashboard-design.attribute.chart.seriesDataLabel') }}</ElDivider>
                      <div
                        v-for="(_series, sIndex) in formData.seriesData || []"
                        :key="sIndex"
                        class="mb-3 rounded border border-gray-200 p-2"
                      >
                        <div class="mb-2 flex items-center justify-between">
                          <ElInput
                            v-model="(localSeriesNames as any)[sIndex]"
                            :placeholder="$t('dashboard-design.attribute.chart.placeholder.seriesName')"
                            size="small"
                            class="w-32"
                            @blur="
                              updateSeriesName(
                                sIndex,
                                (localSeriesNames as any)[sIndex] || '',
                              )
                            "
                          />
                          <ElButton
                            v-if="(formData.seriesData || []).length > 1"
                            size="small"
                            type="danger"
                            text
                            @click="removeSeries(sIndex)"
                          >
                            <Trash2 class="h-3.5 w-3.5" />
                          </ElButton>
                        </div>
                        <ElInput
                          type="textarea"
                          :rows="2"
                          v-model="(localSeriesData as any)[sIndex]"
                          :placeholder="$t('dashboard-design.attribute.chart.placeholder.seriesData')"
                          @blur="
                            updateSeriesData(
                              sIndex,
                              (localSeriesData as any)[sIndex] || '',
                            )
                          "
                        />
                      </div>
                      <ElButton
                        size="small"
                        type="primary"
                        text
                        class="w-full"
                        @click="addSeries"
                      >
                        <Plus class="mr-1 h-3.5 w-3.5" />
                        {{ $t('dashboard-design.attribute.chart.addSeries') }}
                      </ElButton>
                    </template>

                    <!-- 饼图静态数据 -->
                    <template v-else-if="activeWidget.type === 'chart-pie'">
                      <ElDivider content-position="left">{{ $t('dashboard-design.attribute.chart.dataItem') }}</ElDivider>
                      <div
                        v-for="(item, pIndex) in formData.seriesData || []"
                        :key="pIndex"
                        class="mb-2 flex items-center gap-2"
                      >
                        <ElInput
                          :model-value="item.name"
                          :placeholder="$t('dashboard-design.attribute.placeholder.title')"
                          size="small"
                          class="flex-1"
                          @change="
                            (val: string) => updatePieItem(pIndex as any, 'name', val)
                          "
                        />
                        <ElInputNumber
                          :model-value="item.value"
                          :placeholder="$t('dashboard-design.attribute.chart.numerical')"
                          size="small"
                          :min="0"
                          controls-position="right"
                          class="w-24"
                          @change="
                            (val: number | undefined) =>
                              updatePieItem(pIndex as any, 'value', val || 0)
                          "
                        />
                        <ElButton
                          v-if="(formData.seriesData || []).length > 1"
                          size="small"
                          type="danger"
                          text
                          @click="removePieItem(pIndex as any)"
                        >
                          <Trash2 class="h-3.5 w-3.5" />
                        </ElButton>
                      </div>
                      <ElButton
                        size="small"
                        type="primary"
                        text
                        class="w-full"
                        @click="addPieItem"
                      >
                        <Plus class="mr-1 h-3.5 w-3.5" />
                        {{ $t('dashboard-design.attribute.chart.addItem') }}
                      </ElButton>
                    </template>

                    <!-- 漏斗图静态数据（与饼图类似） -->
                    <template v-else-if="activeWidget.type === 'chart-funnel'">
                      <ElDivider content-position="left">{{ $t('dashboard-design.attribute.chart.dataItem') }}</ElDivider>
                      <div
                        v-for="(item, fIndex) in formData.seriesData || []"
                        :key="fIndex"
                        class="mb-2 flex items-center gap-2"
                      >
                        <ElInput
                          :model-value="item.name"
                          :placeholder="$t('dashboard-design.attribute.placeholder.title')"
                          size="small"
                          class="flex-1"
                          @change="
                            (val: string) => updatePieItem(fIndex as any, 'name', val)
                          "
                        />
                        <ElInputNumber
                          :model-value="item.value"
                          :placeholder="$t('dashboard-design.attribute.chart.numerical')"
                          size="small"
                          :min="0"
                          controls-position="right"
                          class="w-24"
                          @change="
                            (val: number | undefined) =>
                              updatePieItem(fIndex as any, 'value', val || 0)
                          "
                        />
                        <ElButton
                          v-if="(formData.seriesData || []).length > 1"
                          size="small"
                          type="danger"
                          text
                          @click="removePieItem(fIndex as any)"
                        >
                          <Trash2 class="h-3.5 w-3.5" />
                        </ElButton>
                      </div>
                      <ElButton
                        size="small"
                        type="primary"
                        text
                        class="w-full"
                        @click="addPieItem"
                      >
                        <Plus class="mr-1 h-3.5 w-3.5" />
                        {{ $t('dashboard-design.attribute.chart.addItem') }}
                      </ElButton>
                    </template>

                    <!-- 雷达图静态数据 -->
                    <template v-else-if="activeWidget.type === 'chart-radar'">
                      <div class="text-muted-foreground mb-2 text-xs">
                        {{ $t('dashboard-design.attribute.chart.radarTip') }}
                      </div>
                    </template>

                    <!-- 散点图静态数据 -->
                    <template v-else-if="activeWidget.type === 'chart-scatter'">
                      <div class="text-muted-foreground mb-2 text-xs">
                        {{ $t('dashboard-design.attribute.chart.scatterTip') }}
                      </div>
                    </template>

                    <!-- 仪表盘静态数据 -->
                    <template v-else-if="activeWidget.type === 'chart-ring'">
                      <div class="text-muted-foreground text-xs">
                        {{ $t('dashboard-design.attribute.chart.ringTip') }}
                      </div>
                    </template>

                    <template v-else-if="activeWidget.type === 'chart-heatmap'">
                      <div class="text-muted-foreground text-xs">
                        {{ $t('dashboard-design.attribute.chart.heatmapTip') }}
                      </div>
                    </template>

                    <template v-else-if="activeWidget.type === 'chart-kline'">
                      <div class="text-muted-foreground text-xs">
                        {{ $t('dashboard-design.attribute.chart.klineTip') }}
                      </div>
                    </template>

                    <template v-else-if="activeWidget.type === 'chart-sankey'">
                      <div class="text-muted-foreground text-xs">
                        {{ $t('dashboard-design.attribute.chart.sankeyTip') }}
                      </div>
                    </template>

                    <template v-else-if="activeWidget.type === 'chart-gauge'">
                      <div class="text-muted-foreground text-xs">
                        {{ $t('dashboard-design.attribute.chart.gaugeTip') }}
                      </div>
                    </template>
                  </template>
                </template>

                <!-- 非图表组件的静态数据编辑 -->
                <template v-else>
                  <!-- 待办列表 -->
                  <template v-if="activeWidget.type === 'todo-list'">
                    <div class="mb-3 flex items-center justify-between">
                      <span class="text-muted-foreground text-xs"
                        >{{ $t('dashboard-design.attribute.chart.dataEditMode') }}</span
                      >
                      <ElRadioGroup v-model="staticDataEditMode" size="small">
                        <ElRadioButton value="form">{{ $t('dashboard-design.attribute.chart.dataEditForm') }}</ElRadioButton>
                        <ElRadioButton value="json">{{ $t('dashboard-design.attribute.chart.dataEditJson') }}</ElRadioButton>
                      </ElRadioGroup>
                    </div>
                    <template v-if="staticDataEditMode === 'json'">
                      <ElInput
                        type="textarea"
                        :rows="10"
                        :model-value="
                          JSON.stringify(formData.items || [], null, 2)
                        "
                        :placeholder="$t('dashboard-design.attribute.chart.jsonPlaceholder')"
                        class="font-mono text-xs"
                        @change="
                          (val: string) => {
                            try {
                              updateProps('items', JSON.parse(val));
                            } catch {}
                          }
                        "
                      />
                    </template>
                    <template v-else>
                      <ElDivider content-position="left">{{ $t('dashboard-design.attribute.widget.todo.items') }}</ElDivider>
                      <div
                        v-for="(item, idx) in formData.items || []"
                        :key="idx"
                        class="mb-2 rounded border border-gray-200 p-2"
                      >
                        <div class="mb-1 flex items-center gap-2">
                          <ElInput
                            :model-value="item.title"
                            :placeholder="$t('dashboard-design.attribute.placeholder.title')"
                            size="small"
                            class="flex-1"
                            @change="
                              (val: string) =>
                                updateListItem('items', idx as any, 'title', val)
                            "
                          />
                          <ElButton
                            size="small"
                            type="danger"
                            text
                            @click="removeListItem('items', idx as any)"
                          >
                            <Trash2 class="h-3.5 w-3.5" />
                          </ElButton>
                        </div>
                        <div class="flex items-center gap-2">
                          <ElSelect
                            :model-value="item.priority"
                            size="small"
                            class="w-20"
                            @change="
                              (val: string) =>
                                updateListItem('items', idx as any, 'priority', val)
                            "
                          >
                            <ElOption :label="$t('dashboard-design.widget.todo.priority.high')" value="high" />
                            <ElOption :label="$t('dashboard-design.widget.todo.priority.medium')" value="medium" />
                            <ElOption :label="$t('dashboard-design.widget.todo.priority.low')" value="low" />
                          </ElSelect>
                          <ElSwitch
                            :model-value="item.done"
                            size="small"
                            :active-text="$t('dashboard-design.attribute.widget.todo.done')"
                            @change="
                              (val: string | number | boolean) =>
                                updateListItem('items', idx as any, 'done', val)
                            "
                          />
                        </div>
                      </div>
                      <ElButton
                        size="small"
                        type="primary"
                        text
                        class="w-full"
                        @click="addTodoItem"
                      >
                        <Plus class="mr-1 h-3.5 w-3.5" />
                        {{ $t('dashboard-design.attribute.widget.todo.add') }}
                      </ElButton>
                    </template>
                  </template>

                  <!-- 通知列表 - 使用实际数据，无需配置 -->
                  <template v-else-if="activeWidget.type === 'notice-list'">
                    <div class="text-muted-foreground text-xs">
                      {{ $t('dashboard-design.attribute.widget.notice.tip') }}
                    </div>
                    <ElFormItem :label="$t('dashboard-design.attribute.widget.notice.limit')" class="mt-3">
                      <ElInputNumber
                        v-model="formData.limit"
                        :min="1"
                        :max="20"
                        controls-position="right"
                        class="w-full"
                        @change="
                          (val: number | undefined) =>
                            updateProps('limit', val || 5)
                        "
                      />
                    </ElFormItem>
                  </template>

                  <!-- 公告列表 - 使用实际数据，无需配置 -->
                  <template
                    v-else-if="activeWidget.type === 'announcement-list'"
                  >
                    <div class="text-muted-foreground text-xs">
                      {{ $t('dashboard-design.attribute.widget.announcement.tip') }}
                    </div>
                    <ElFormItem :label="$t('dashboard-design.attribute.widget.announcement.limit')" class="mt-3">
                      <ElInputNumber
                        v-model="formData.limit"
                        :min="1"
                        :max="20"
                        controls-position="right"
                        class="w-full"
                        @change="
                          (val: number | undefined) =>
                            updateProps('limit', val || 5)
                        "
                      />
                    </ElFormItem>
                  </template>

                  <!-- 排行榜 -->
                  <template v-else-if="activeWidget.type === 'ranking-list'">
                    <div class="mb-3 flex items-center justify-between">
                      <span class="text-muted-foreground text-xs"
                        >{{ $t('dashboard-design.attribute.chart.dataEditMode') }}</span
                      >
                      <ElRadioGroup v-model="staticDataEditMode" size="small">
                        <ElRadioButton value="form">{{ $t('dashboard-design.attribute.chart.dataEditForm') }}</ElRadioButton>
                        <ElRadioButton value="json">{{ $t('dashboard-design.attribute.chart.dataEditJson') }}</ElRadioButton>
                      </ElRadioGroup>
                    </div>
                    <template v-if="staticDataEditMode === 'json'">
                      <ElInput
                        type="textarea"
                        :rows="10"
                        :model-value="
                          JSON.stringify(formData.items || [], null, 2)
                        "
                        :placeholder="$t('dashboard-design.attribute.chart.jsonPlaceholder')"
                        class="font-mono text-xs"
                        @change="
                          (val: string) => {
                            try {
                              updateProps('items', JSON.parse(val));
                            } catch {}
                          }
                        "
                      />
                    </template>
                    <template v-else>
                      <ElDivider content-position="left">{{ $t('dashboard-design.attribute.widget.ranking.items') }}</ElDivider>
                      <div
                        v-for="(item, idx) in formData.items || []"
                        :key="idx"
                        class="mb-2 flex items-center gap-2"
                      >
                        <span
                          class="text-muted-foreground w-6 text-center text-xs"
                          >{{ idx + 1 }}</span
                        >
                        <ElInput
                          :model-value="item.name"
                          :placeholder="$t('dashboard-design.attribute.placeholder.name')"
                          size="small"
                          class="flex-1"
                          @change="
                            (val: string) => updateRankingItem(idx, 'name', val)
                          "
                        />
                        <ElInputNumber
                          :model-value="item.value"
                          :placeholder="$t('dashboard-design.attribute.chart.numerical')"
                          size="small"
                          :min="0"
                          controls-position="right"
                          class="w-24"
                          @change="
                            (val: number | undefined) =>
                              updateRankingItem(idx, 'value', val || 0)
                          "
                        />
                        <ElButton
                          size="small"
                          type="danger"
                          text
                          @click="removeListItem('items', idx)"
                        >
                          <Trash2 class="h-3.5 w-3.5" />
                        </ElButton>
                      </div>
                      <ElButton
                        size="small"
                        type="primary"
                        text
                        class="w-full"
                        @click="addRankingItem"
                      >
                        <Plus class="mr-1 h-3.5 w-3.5" />
                        {{ $t('dashboard-design.attribute.widget.ranking.add') }}
                      </ElButton>
                    </template>
                  </template>

                  <!-- 快捷入口 -->
                  <template v-else-if="activeWidget.type === 'quick-links'">
                    <div class="text-muted-foreground mb-3 text-xs">
                      {{ $t('dashboard-design.attribute.widget.quickLinks.tip') }}
                    </div>
                    <!-- 网格可视化配置 -->
                    <ElScrollbar class="quick-links-scrollbar">
                      <div
                        class="quick-links-grid gap-1.5 rounded-lg border border-dashed border-gray-300 p-2 dark:border-gray-600"
                        :style="{
                          display: 'grid',
                          gridTemplateColumns: `repeat(${formData.columns || 4}, minmax(48px, 1fr))`,
                          minWidth: `${(formData.columns || 4) * 56}px`,
                        }"
                      >
                        <div
                          v-for="idx in (formData.columns || 4) *
                          (formData.rows || 2)"
                          :key="idx"
                          class="quick-link-cell hover:border-primary hover:bg-primary/5 group relative flex cursor-pointer flex-col items-center justify-center gap-1 rounded-md border border-gray-200 p-2 transition-all dark:border-gray-700"
                          :class="{
                            'border-solid bg-gray-50 dark:bg-gray-800':
                              getMenuAtIndex(idx - 1),
                          }"
                          @click="openMenuSelectorForCell(idx - 1)"
                        >
                          <template v-if="getMenuAtIndex(idx - 1)">
                            <IconifyIcon
                              v-if="getMenuAtIndex(idx - 1)?.icon"
                              :icon="getMenuAtIndex(idx - 1).icon"
                              class="text-primary h-5 w-5"
                            />
                            <div
                              v-else
                              class="text-primary flex h-5 w-5 items-center justify-center"
                            >
                              <span class="text-xs font-bold">{{
                                (getMenuAtIndex(idx - 1)?.title || '')[0]
                              }}</span>
                            </div>
                            <span
                              class="text-muted-foreground w-full truncate text-center text-xs"
                            >
                              {{ getMenuAtIndex(idx - 1)?.title }}
                            </span>
                            <!-- 删除按钮 -->
                            <button
                              class="absolute -right-1 -top-1 hidden h-4 w-4 items-center justify-center rounded-full bg-red-500 text-white group-hover:flex"
                              @click.stop="removeMenuAtIndex(idx - 1)"
                            >
                              <span class="text-xs leading-none">×</span>
                            </button>
                          </template>
                          <template v-else>
                            <Plus
                              class="text-muted-foreground h-4 w-4 opacity-40"
                            />
                            <span
                              class="text-muted-foreground text-xs opacity-40"
                              >{{ $t('dashboard-design.add') }}</span
                            >
                          </template>
                        </div>
                      </div>
                    </ElScrollbar>
                  </template>

                  <!-- 数据表格 -->
                  <template v-else-if="activeWidget.type === 'data-table'">
                    <div class="mb-3 flex items-center justify-between">
                      <span class="text-muted-foreground text-xs"
                        >{{ $t('dashboard-design.attribute.chart.dataEditMode') }}</span
                      >
                      <ElRadioGroup v-model="staticDataEditMode" size="small">
                        <ElRadioButton value="form">{{ $t('dashboard-design.attribute.chart.dataEditForm') }}</ElRadioButton>
                        <ElRadioButton value="json">{{ $t('dashboard-design.attribute.chart.dataEditJson') }}</ElRadioButton>
                      </ElRadioGroup>
                    </div>
                    <template v-if="staticDataEditMode === 'json'">
                      <ElDivider content-position="left">{{ $t('dashboard-design.attribute.widget.table.columnConfig') }}</ElDivider>
                      <ElInput
                        type="textarea"
                        :rows="5"
                        :model-value="
                          JSON.stringify(formData.columns || [], null, 2)
                        "
                        :placeholder="$t('dashboard-design.attribute.widget.table.columnConfigJson')"
                        class="font-mono text-xs"
                        @change="
                          (val: string) => {
                            try {
                              updateProps('columns', JSON.parse(val));
                            } catch {}
                          }
                        "
                      />
                      <ElDivider content-position="left">{{ $t('dashboard-design.attribute.widget.table.tableData') }}</ElDivider>
                      <ElInput
                        type="textarea"
                        :rows="8"
                        :model-value="
                          JSON.stringify(formData.data || [], null, 2)
                        "
                        :placeholder="$t('dashboard-design.attribute.widget.table.tableDataJson')"
                        class="font-mono text-xs"
                        @change="
                          (val: string) => {
                            try {
                              updateProps('data', JSON.parse(val));
                            } catch {}
                          }
                        "
                      />
                    </template>
                    <template v-else>
                      <div class="text-muted-foreground text-xs">
                        {{ $t('dashboard-design.attribute.widget.table.complexDataTip') }}
                      </div>
                    </template>
                  </template>

                  <!-- 图片轮播 - 静态数据模式 -->
                  <template v-else-if="activeWidget.type === 'image-carousel'">
                    <div class="mb-3 flex items-center justify-between">
                      <span class="text-muted-foreground text-xs"
                        >{{ $t('dashboard-design.attribute.chart.dataEditMode') }}</span
                      >
                      <ElRadioGroup v-model="staticDataEditMode" size="small">
                        <ElRadioButton value="form">{{ $t('dashboard-design.attribute.chart.dataEditForm') }}</ElRadioButton>
                        <ElRadioButton value="json">{{ $t('dashboard-design.attribute.chart.dataEditJson') }}</ElRadioButton>
                      </ElRadioGroup>
                    </div>
                    <template v-if="staticDataEditMode === 'json'">
                      <ElInput
                        type="textarea"
                        :rows="10"
                        :model-value="
                          JSON.stringify(formData.images || [], null, 2)
                        "
                        :placeholder="$t('dashboard-design.attribute.chart.jsonPlaceholder')"
                        class="font-mono text-xs"
                        @change="
                          (val: string) => {
                            try {
                              updateProps('images', JSON.parse(val));
                            } catch {}
                          }
                        "
                      />
                    </template>
                    <template v-else>
                      <ElDivider content-position="left">{{ $t('dashboard-design.attribute.widget.carousel.imageList') }}</ElDivider>
                      <div
                        v-for="(img, idx) in formData.images || []"
                        :key="idx"
                        class="mb-2 rounded border border-gray-200 p-2"
                      >
                        <div class="mb-1 flex items-center gap-2">
                          <ElInput
                            :model-value="img.title"
                            :placeholder="$t('dashboard-design.attribute.title')"
                            size="small"
                            class="flex-1"
                            @change="
                              (val: string) =>
                                updateImageItem(idx, 'title', val)
                            "
                          />
                          <ElButton
                            size="small"
                            type="danger"
                            text
                            @click="removeListItem('images', idx)"
                          >
                            <Trash2 class="h-3.5 w-3.5" />
                          </ElButton>
                        </div>
                        <ElInput
                          :model-value="img.url"
                          :placeholder="$t('dashboard-design.attribute.widget.image.url')"
                          size="small"
                          class="mb-1"
                          @change="
                            (val: string) => updateImageItem(idx, 'url', val)
                          "
                        />
                        <ElInput
                          :model-value="img.link"
                          :placeholder="$t('dashboard-design.attribute.widget.image.link')"
                          size="small"
                          @change="
                            (val: string) => updateImageItem(idx, 'link', val)
                          "
                        />
                      </div>
                      <ElButton
                        size="small"
                        type="primary"
                        text
                        class="w-full"
                        @click="addImageItem"
                      >
                        <Plus class="mr-1 h-3.5 w-3.5" />
                        {{ $t('dashboard-design.attribute.widget.carousel.addImage') }}
                      </ElButton>
                    </template>
                  </template>

                  <!-- 图片组件 - 静态数据模式 -->
                  <template v-else-if="activeWidget.type === 'image'">
                    <ElDivider content-position="left">{{ $t('dashboard-design.attribute.widget.image.url') }}</ElDivider>
                    <ElFormItem :label="$t('dashboard-design.attribute.widget.image.url')">
                      <ElInput
                        v-model="formData.src"
                        :placeholder="$t('dashboard-design.attribute.widget.image.urlPlaceholder')"
                        @change="(val: string) => updateProps('src', val)"
                      />
                    </ElFormItem>
                    <ElDivider content-position="left">
                      {{ $t('dashboard-design.attribute.widget.image.previewList') }}
                    </ElDivider>
                    <div class="text-muted-foreground mb-2 text-xs">
                      {{ $t('dashboard-design.attribute.widget.image.previewListTip') }}
                    </div>
                    <div
                      v-for="(url, idx) in formData.previewSrcList || []"
                      :key="idx"
                      class="mb-2 flex items-center gap-2"
                    >
                      <ElInput
                        :model-value="url"
                        :placeholder="$t('dashboard-design.attribute.widget.image.url')"
                        size="small"
                        class="flex-1"
                        @change="(val: string) => updatePreviewImage(idx, val)"
                      />
                      <ElButton
                        size="small"
                        type="danger"
                        text
                        @click="removePreviewImage(idx)"
                      >
                        <Trash2 class="h-3.5 w-3.5" />
                      </ElButton>
                    </div>
                    <ElButton
                      size="small"
                      type="primary"
                      text
                      class="w-full"
                      @click="addPreviewImage"
                    >
                      <Plus class="mr-1 h-3.5 w-3.5" />
                      {{ $t('dashboard-design.attribute.widget.image.addImage') }}
                    </ElButton>
                  </template>

                  <!-- 统计卡片 -->
                  <template v-else-if="activeWidget.type === 'stat-card'">
                    <div class="mb-3 flex items-center justify-between">
                      <span class="text-muted-foreground text-xs"
                        >{{ $t('dashboard-design.attribute.chart.dataEditMode') }}</span
                      >
                      <ElRadioGroup v-model="staticDataEditMode" size="small">
                        <ElRadioButton value="form">{{ $t('dashboard-design.attribute.chart.dataEditForm') }}</ElRadioButton>
                        <ElRadioButton value="json">{{ $t('dashboard-design.attribute.chart.dataEditJson') }}</ElRadioButton>
                      </ElRadioGroup>
                    </div>
                    <template v-if="staticDataEditMode === 'json'">
                      <ElInput
                        type="textarea"
                        :rows="12"
                        :model-value="
                          JSON.stringify(
                            {
                              value: formData.value,
                              prefix: formData.prefix,
                              suffix: formData.suffix,
                              trend: formData.trend,
                              trendLabel: formData.trendLabel,
                            },
                            null,
                            2,
                          )
                        "
                        :placeholder="$t('dashboard-design.attribute.chart.jsonPlaceholder')"
                        class="font-mono text-xs"
                        @change="
                          (val: string) => {
                            try {
                              const data = JSON.parse(val);
                              if (data.value !== undefined)
                                updateProps('value', data.value);
                              if (data.prefix !== undefined)
                                updateProps('prefix', data.prefix);
                              if (data.suffix !== undefined)
                                updateProps('suffix', data.suffix);
                              if (data.trend !== undefined)
                                updateProps('trend', data.trend);
                              if (data.trendLabel !== undefined)
                                updateProps('trendLabel', data.trendLabel);
                            } catch {}
                          }
                        "
                      />
                    </template>
                    <template v-else>
                      <ElDivider content-position="left">{{ $t('dashboard-design.attribute.dataConfig') }}</ElDivider>
                      <ElFormItem :label="$t('dashboard-design.attribute.chart.currentValue')">
                        <ElInputNumber
                          v-model="formData.value"
                          controls-position="right"
                          class="w-full"
                          @change="
                            (val: number | undefined) =>
                              updateProps('value', val || 0)
                          "
                        />
                      </ElFormItem>
                      <ElFormItem :label="$t('dashboard-design.attribute.chart.prefix')">
                        <ElInput
                          v-model="formData.prefix"
                          :placeholder="$t('dashboard-design.attribute.chart.placeholder.prefix')"
                          @change="(val: string) => updateProps('prefix', val)"
                        />
                      </ElFormItem>
                      <ElFormItem :label="$t('dashboard-design.attribute.chart.suffix')">
                        <ElInput
                          v-model="formData.suffix"
                          :placeholder="$t('dashboard-design.attribute.chart.placeholder.suffix')"
                          @change="(val: string) => updateProps('suffix', val)"
                        />
                      </ElFormItem>
                      <ElDivider content-position="left">{{ $t('dashboard-design.attribute.chart.trendConfig') }}</ElDivider>
                      <ElFormItem :label="$t('dashboard-design.attribute.chart.trendValue')">
                        <ElInputNumber
                          v-model="formData.trend"
                          controls-position="right"
                          class="w-full"
                          @change="
                            (val: number | undefined) =>
                              updateProps('trend', val || 0)
                          "
                        />
                        <div class="text-muted-foreground mt-1 text-xs">
                          {{ $t('dashboard-design.attribute.chart.trendTip') }}
                        </div>
                      </ElFormItem>
                      <ElFormItem :label="$t('dashboard-design.attribute.chart.trendLabel')">
                        <ElInput
                          v-model="formData.trendLabel"
                          :placeholder="$t('dashboard-design.attribute.chart.placeholder.trendLabel')"
                          @change="
                            (val: string) => updateProps('trendLabel', val)
                          "
                        />
                      </ElFormItem>
                    </template>
                  </template>

                  <!-- 进度卡片 -->
                  <template v-else-if="activeWidget.type === 'progress-card'">
                    <ElDivider content-position="left">{{ $t('dashboard-design.attribute.dataConfig') }}</ElDivider>
                    <ElFormItem :label="$t('dashboard-design.attribute.chart.showProgress')">
                      <ElInputNumber
                        v-model="formData.percentage"
                        :min="0"
                        :max="100"
                        controls-position="right"
                        class="w-full"
                        @change="
                          (val: number | undefined) =>
                            updateProps('percentage', val || 0)
                        "
                      />
                    </ElFormItem>
                  </template>

                  <!-- iframe -->
                  <template v-else-if="activeWidget.type === 'iframe'">
                    <ElDivider content-position="left">{{ $t('dashboard-design.attribute.widget.iframe.pageAddress') }}</ElDivider>
                    <ElFormItem label="URL">
                      <ElInput
                        v-model="formData.url"
                        placeholder="https://example.com"
                        @change="(val: string) => updateProps('url', val)"
                      />
                    </ElFormItem>
                  </template>

                  <!-- 视频播放器 - 静态数据模式 -->
                  <template v-else-if="activeWidget.type === 'video-player'">
                    <ElDivider content-position="left">{{ $t('dashboard-design.attribute.widget.video.videoAddress') }}</ElDivider>
                    <ElFormItem :label="$t('dashboard-design.attribute.widget.video.videoAddress')">
                      <ElInput
                        v-model="formData.url"
                        placeholder="https://example.com/video.mp4"
                        @change="(val: string) => updateProps('url', val)"
                      />
                    </ElFormItem>
                    <ElFormItem :label="$t('dashboard-design.attribute.widget.video.poster')">
                      <ElInput
                        v-model="formData.poster"
                        :placeholder="$t('dashboard-design.attribute.widget.video.posterPlaceholder')"
                        @change="(val: string) => updateProps('poster', val)"
                      />
                    </ElFormItem>
                  </template>

                  <!-- 其他组件 -->
                  <template v-else>
                    <div class="text-muted-foreground text-xs">
                      {{ $t('dashboard-design.attribute.widget.common.staticDataTip') }}
                    </div>
                  </template>
                </template>
              </template>

              <!-- 图片上传模式 -->
              <template v-if="dataSourceForm.type === 'upload'">
                <!-- 图片轮播 - 上传模式 -->
                <template v-if="activeWidget.type === 'image-carousel'">
                  <ElDivider content-position="left">{{ $t('dashboard-design.attribute.widget.carousel.selectFromGallery') }}</ElDivider>
                  <ImageSelector
                    :multiple="true"
                    :size="100"
                    class="mb-3"
                    @change="handleCarouselImageSelect"
                  />
                  <ElDivider content-position="left">{{ $t('dashboard-design.attribute.widget.carousel.selectedImages') }}</ElDivider>
                  <div
                    v-for="(img, idx) in formData.images || []"
                    :key="idx"
                    class="mb-2 flex items-center gap-2 rounded border border-gray-200 p-2 dark:border-gray-700"
                  >
                    <div class="flex-1 truncate text-xs">{{ img.url }}</div>
                    <ElButton
                      size="small"
                      type="danger"
                      text
                      @click="removeListItem('images', idx)"
                    >
                      <Trash2 class="h-3.5 w-3.5" />
                    </ElButton>
                  </div>
                  <div
                    v-if="(formData.images || []).length === 0"
                    class="text-muted-foreground py-4 text-center text-xs"
                  >
                    {{ $t('dashboard-design.attribute.widget.carousel.selectTip') }}
                  </div>
                </template>

                <!-- 图片组件 - 上传模式 -->
                <template v-else-if="activeWidget.type === 'image'">
                  <ElDivider content-position="left">{{ $t('dashboard-design.attribute.widget.image.mainImage') }}</ElDivider>
                  <ImageSelector
                    :size="100"
                    class="mb-3"
                    @change="handleImageSelect"
                  />
                  <div
                    v-if="formData.src"
                    class="text-muted-foreground mb-3 truncate text-xs"
                  >
                    {{ formData.src }}
                  </div>
                  <ElDivider content-position="left"> {{ $t('dashboard-design.attribute.widget.image.previewList') }} </ElDivider>
                  <div class="text-muted-foreground mb-2 text-xs">
                    {{ $t('dashboard-design.attribute.widget.image.previewListTip') }}
                  </div>
                  <ImageSelector
                    :multiple="true"
                    :size="100"
                    class="mb-2"
                    @change="handlePreviewImageSelect"
                  />
                  <div
                    v-for="(img, idx) in formData.previewImages || []"
                    :key="idx"
                    class="mb-1 flex items-center gap-2"
                  >
                    <div class="flex-1 truncate text-xs">{{ img }}</div>
                    <ElButton
                      size="small"
                      type="danger"
                      text
                      @click="removePreviewImage(idx)"
                    >
                      <Trash2 class="h-3.5 w-3.5" />
                    </ElButton>
                  </div>
                </template>

                <!-- 视频播放器 - 上传模式 -->
                <template v-else-if="activeWidget.type === 'video-player'">
                  <ElDivider content-position="left"> {{ $t('dashboard-design.attribute.widget.video.selectFromFileLib') }} </ElDivider>
                  <FileSelector
                    :accept="['video/*']"
                    class="mb-3"
                    @change="handleVideoSelect"
                  />
                  <div
                    v-if="formData.url"
                    class="text-muted-foreground mb-3 truncate text-xs"
                  >
                    {{ formData.url }}
                  </div>
                  <ElDivider content-position="left">{{ $t('dashboard-design.attribute.widget.video.poster') }}</ElDivider>
                  <ImageSelector
                    :size="100"
                    class="mb-2"
                    @change="
                      (fileId: string | string[] | undefined) => {
                        if (fileId) {
                          const id = Array.isArray(fileId) ? fileId[0] : fileId;
                          if (id) updateProps('poster', `file://${id}`);
                        }
                      }
                    "
                  />
                  <div
                    v-if="formData.poster"
                    class="text-muted-foreground mb-3 truncate text-xs"
                  >
                    {{ formData.poster }}
                  </div>
                </template>
              </template>
            </template>

            <!-- 样式配置 -->
            <template v-if="activeTab === 'style'">
              <!-- 背景 -->
              <ElDivider content-position="left">{{ $t('dashboard-design.attribute.background') }}</ElDivider>
              <ElFormItem :label="$t('dashboard-design.attribute.backgroundColor')">
                <div class="flex items-center gap-2">
                  <ElColorPicker
                    v-model="styleForm.backgroundColor"
                    show-alpha
                    @change="
                      (val: string | null) =>
                        updateStyle('backgroundColor', val || '')
                    "
                  />
                  <ElButton
                    v-if="styleForm.backgroundColor"
                    size="small"
                    text
                    @click="updateStyle('backgroundColor', '')"
                  >
                    {{ $t('dashboard-design.clean') }}
                  </ElButton>
                </div>
              </ElFormItem>

              <!-- 边框 -->
              <ElDivider content-position="left">{{ $t('dashboard-design.attribute.border') }}</ElDivider>
              <ElFormItem :label="$t('dashboard-design.attribute.borderWidth')">
                <ElInputNumber
                  v-model="styleForm.borderWidth"
                  :min="0"
                  :max="10"
                  controls-position="right"
                  class="w-full"
                  @change="
                    (val: number | undefined) =>
                      updateStyle('borderWidth', val || 0)
                  "
                />
              </ElFormItem>
              <ElFormItem
                v-if="styleForm.borderWidth && styleForm.borderWidth > 0"
                :label="$t('dashboard-design.attribute.borderColor')"
              >
                <ElColorPicker
                  v-model="styleForm.borderColor"
                  @change="
                    (val: string | null) =>
                      updateStyle('borderColor', val || '')
                  "
                />
              </ElFormItem>
              <ElFormItem
                v-if="styleForm.borderWidth && styleForm.borderWidth > 0"
                :label="$t('dashboard-design.attribute.borderStyleLabel')"
              >
                <ElSelect
                  v-model="styleForm.borderStyle"
                  class="w-full"
                  @change="(val: string) => updateStyle('borderStyle', val)"
                >
                  <ElOption
                    v-for="opt in borderStyleOptions"
                    :key="opt.value"
                    :label="opt.label"
                    :value="opt.value"
                  />
                </ElSelect>
              </ElFormItem>
              <ElFormItem :label="$t('dashboard-design.attribute.borderRadius')">
                <ElInputNumber
                  v-model="styleForm.borderRadius"
                  :min="0"
                  :max="50"
                  controls-position="right"
                  class="w-full"
                  @change="
                    (val: number | undefined) =>
                      updateStyle('borderRadius', val || 0)
                  "
                />
              </ElFormItem>

              <!-- 阴影 -->
              <ElDivider content-position="left">{{ $t('dashboard-design.attribute.shadow') }}</ElDivider>
              <ElFormItem :label="$t('dashboard-design.attribute.enableShadow')">
                <ElSwitch
                  v-model="styleForm.shadowEnabled"
                  @change="
                    (val: string | number | boolean) =>
                      updateStyle('shadowEnabled', val)
                  "
                />
              </ElFormItem>
              <template v-if="styleForm.shadowEnabled">
                <ElFormItem :label="$t('dashboard-design.attribute.shadowColor')">
                  <ElColorPicker
                    v-model="styleForm.shadowColor"
                    show-alpha
                    @change="
                      (val: string | null) =>
                        updateStyle('shadowColor', val || 'rgba(0,0,0,0.1)')
                    "
                  />
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.shadowBlur')">
                  <ElInputNumber
                    v-model="styleForm.shadowBlur"
                    :min="0"
                    :max="50"
                    controls-position="right"
                    class="w-full"
                    @change="
                      (val: number | undefined) =>
                        updateStyle('shadowBlur', val || 0)
                    "
                  />
                </ElFormItem>
              </template>

              <!-- 图表布局（仅有坐标轴的图表显示） -->
              <template
                v-if="
                  [
                    'chart-line',
                    'chart-bar',
                    'chart-area',
                    'chart-scatter',
                    'chart-heatmap',
                    'chart-kline',
                  ].includes(activeWidget.type)
                "
              >
                <ElDivider content-position="left">{{ $t('dashboard-design.attribute.chartLayout') }}</ElDivider>
                <ElFormItem :label="$t('dashboard-design.attribute.margin.left')">
                  <ElInputNumber
                    v-model="formData.gridLeft"
                    :min="0"
                    :max="30"
                    controls-position="right"
                    class="w-full"
                    @change="
                      (val: number | undefined) => updateProps('gridLeft', val)
                    "
                  />
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.margin.right')">
                  <ElInputNumber
                    v-model="formData.gridRight"
                    :min="0"
                    :max="30"
                    controls-position="right"
                    class="w-full"
                    @change="
                      (val: number | undefined) => updateProps('gridRight', val)
                    "
                  />
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.margin.top')">
                  <ElInputNumber
                    v-model="formData.gridTop"
                    :min="0"
                    :max="30"
                    controls-position="right"
                    class="w-full"
                    @change="
                      (val: number | undefined) => updateProps('gridTop', val)
                    "
                  />
                </ElFormItem>
                <ElFormItem :label="$t('dashboard-design.attribute.margin.bottom')">
                  <ElInputNumber
                    v-model="formData.gridBottom"
                    :min="0"
                    :max="30"
                    controls-position="right"
                    class="w-full"
                    @change="
                      (val: number | undefined) =>
                        updateProps('gridBottom', val)
                    "
                  />
                </ElFormItem>
              </template>
            </template>
          </ElForm>
        </div>
      </ElScrollbar>
    </div>

    <!-- 右侧导航栏 -->
    <div class="flex w-14 flex-col bg-gray-50 dark:bg-gray-800">
      <!-- 导航按钮 -->
      <button
        class="nav-btn"
        :class="{
          active: activeTab === 'basic' && !isPanelCollapsed && activeWidget,
        }"
        @click="
          activeTab = 'basic';
          isPanelCollapsed = false;
        "
      >
        <Settings class="h-4 w-4" />
        <span>{{ $t('dashboard-design.attribute.tabs.basic') }}</span>
      </button>
      <button
        class="nav-btn"
        :class="{
          active:
            activeTab === 'dataSource' && !isPanelCollapsed && activeWidget,
        }"
        @click="
          activeTab = 'dataSource';
          isPanelCollapsed = false;
        "
      >
        <Database class="h-4 w-4" />
        <span>{{ $t('dashboard-design.attribute.tabs.data') }}</span>
      </button>
      <button
        class="nav-btn"
        :class="{
          active: activeTab === 'style' && !isPanelCollapsed && activeWidget,
        }"
        @click="
          activeTab = 'style';
          isPanelCollapsed = false;
        "
      >
        <Palette class="h-4 w-4" />
        <span>{{ $t('dashboard-design.attribute.tabs.style') }}</span>
      </button>

      <!-- 占位，将折叠按钮推到底部 -->
      <div class="flex-1"></div>

      <!-- 折叠按钮 -->
      <button
        class="collapse-btn"
        @click="isPanelCollapsed = !isPanelCollapsed"
      >
        <ChevronsRight v-if="isPanelCollapsed" class="h-4 w-4" />
        <ChevronsLeft v-else class="h-4 w-4" />
      </button>
    </div>
  </div>

  <!-- 菜单选择弹窗 -->
  <ZqMenuSelector
    ref="menuSelectorRef"
    mode="popup"
    :dialog-title="$t('dashboard-design.attribute.widget.quickLinks.selectMenu')"
    dialog-width="400px"
    @select="handleMenuSelect"
  />
</template>

<style scoped>
.attribute-panel {
  overflow: hidden;
  background-color: var(--el-bg-color);
  border-radius: 8px;
  transition: width 0.2s ease;
}

:deep(.el-form-item) {
  margin-bottom: 12px;
}

:deep(.el-form-item__label) {
  padding-bottom: 4px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
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

/* 右侧导航按钮 */
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

.nav-btn.active::before {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  width: 2px;
  content: '';
  background-color: var(--el-color-primary);
}

/* 快捷入口网格配置 */
.quick-link-cell {
  min-height: 50px;
  aspect-ratio: 1;
}
</style>
