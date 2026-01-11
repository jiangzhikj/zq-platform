import { $t } from '@vben/locales';

import type { DataSource } from '#/api/core/data-source';

/**
 * 数据源类型选项
 */
export const getSourceTypeOptions = () => [
  { label: $t('data-source.apiInterface'), value: 'api' },
  { label: $t('data-source.sqlQuery'), value: 'sql' },
  { label: $t('data-source.staticData'), value: 'static' },
];

/**
 * 结果类型选项
 */
export const getResultTypeOptions = () => [
  { label: $t('data-source.resultTypeList'), value: 'list', description: $t('data-source.resultTypeListDesc') },
  { label: $t('data-source.resultTypeTree'), value: 'tree', description: $t('data-source.resultTypeTreeDesc') },
  { label: $t('data-source.resultTypeSingleObject'), value: 'object', description: $t('data-source.resultTypeObjectDesc') },
  {
    label: $t('data-source.resultTypeSingleValue'),
    value: 'value',
    description: $t('data-source.resultTypeValueDesc'),
  },
  {
    label: $t('data-source.resultTypeAxisChart'),
    value: 'chart-axis',
    description: $t('data-source.resultTypeChartAxisDesc'),
  },
  { label: $t('data-source.resultTypePieChart'), value: 'chart-pie', description: $t('data-source.resultTypeChartPieDesc') },
  { label: $t('data-source.resultTypeGauge'), value: 'chart-gauge', description: $t('data-source.resultTypeChartGaugeDesc') },
  { label: $t('data-source.resultTypeRadarChart'), value: 'chart-radar', description: $t('data-source.resultTypeChartRadarDesc') },
  { label: $t('data-source.resultTypeScatterChart'), value: 'chart-scatter', description: $t('data-source.resultTypeChartScatterDesc') },
  { label: $t('data-source.resultTypeHeatmap'), value: 'chart-heatmap', description: $t('data-source.resultTypeChartHeatmapDesc') },
];

/**
 * HTTP 方法选项
 */
export const httpMethodOptions = [
  { label: 'GET', value: 'GET' },
  { label: 'POST', value: 'POST' },
];

/**
 * 参数类型选项
 */
export const getParamTypeOptions = () => [
  { label: $t('data-source.paramTypeString'), value: 'string' },
  { label: $t('data-source.paramTypeInteger'), value: 'integer' },
  { label: $t('data-source.paramTypeFloat'), value: 'float' },
  { label: $t('data-source.paramTypeBoolean'), value: 'boolean' },
];

/**
 * 默认数据源配置
 */
export const defaultDataSource: Partial<DataSource> = {
  name: '',
  code: '',
  source_type: 'sql',
  description: '',
  status: true,
  // API 配置
  api_url: '',
  api_method: 'GET',
  api_headers: {},
  api_body: {},
  api_timeout: 30,
  api_data_path: '',
  // SQL 配置
  sql_content: '',
  db_connection: 'default',
  // 静态数据
  static_data: [],
  // 参数
  params: [],
  // 结果处理
  result_type: 'list',
  tree_config: {},
  field_mapping: {},
  chart_config: {},
  // 缓存
  cache_enabled: false,
  cache_ttl: 300,
};
