export { default as DashboardRenderer } from './DashboardRenderer.vue';
// 主页设计器组件导出
export { default as DashboardDesign } from './index.vue';

// Store 和类型导出
export {
  type DashboardConfig,
  type DashboardWidget,
  type DataSourceConfig,
  type DataSourceType,
  useDashboardDesignStore,
  type WidgetMaterial,
  widgetMaterials,
  type WidgetType,
} from './store/dashboardDesignStore';

// 工具函数导出
export { createRefreshTimer, fetchWidgetData } from './utils/dataFetcher';
