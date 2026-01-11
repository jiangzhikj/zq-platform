import type {
  DataSourceConfig,
  FieldMapping,
} from '../store/dashboardDesignStore';

import { requestClient } from '#/api/request';
import { $t } from '@vben/locales';

/**
 * 根据路径获取对象中的值
 * @param obj 对象
 * @param path 路径，如 'data.list' 或 'data.items[0].name'
 */
export function getValueByPath(obj: any, path: string): any {
  if (!obj || !path) return obj;

  const keys = path.replaceAll(/\[(\d+)\]/g, '.$1').split('.');
  let result = obj;

  for (const key of keys) {
    if (result === null || result === undefined) return undefined;
    result = result[key];
  }

  return result;
}

/**
 * 根据路径设置对象中的值
 */
export function setValueByPath(obj: any, path: string, value: any): void {
  if (!obj || !path) return;

  const keys = path.split('.');
  let current = obj;

  for (let i = 0; i < keys.length - 1; i++) {
    const key = keys[i]!;
    if (current[key] === undefined) {
      current[key] = {};
    }
    current = current[key];
  }

  current[keys[keys.length - 1]!] = value;
}

/**
 * 应用字段映射
 */
export function applyFieldMappings(
  data: any,
  mappings: FieldMapping[] | undefined,
  targetProps: Record<string, any>,
): Record<string, any> {
  if (!mappings || mappings.length === 0) {
    return { ...targetProps, ...data };
  }

  const result = { ...targetProps };

  for (const mapping of mappings) {
    const value = getValueByPath(data, mapping.source);
    if (value !== undefined) {
      setValueByPath(result, mapping.target, value);
    }
  }

  return result;
}

/**
 * 数据获取工具
 */
export async function fetchWidgetData(
  dataSource: DataSourceConfig | undefined,
  defaultProps: Record<string, any>,
): Promise<{ data: any; props: Record<string, any> }> {
  if (!dataSource || dataSource.type === 'static') {
    return { data: null, props: defaultProps };
  }

  // 通用数据源类型
  if (dataSource.type === 'dataSource' && dataSource.dataSourceCode) {
    try {
      const response = await requestClient.get(
        `/api/core/data-source/execute/${dataSource.dataSourceCode}`,
      );

      // 后端返回格式是 {data: ...}，需要提取 data 字段
      const rawData = response?.data ?? response;

      // 数据源返回的数据可能是数组或对象（图表数据源返回 {xAxisData, seriesData} 格式）
      const extractedData = dataSource.dataPath
        ? getValueByPath(rawData, dataSource.dataPath)
        : rawData;

      // 检查是否是图表数据格式（包含 xAxisData 或 seriesData 或 indicator 或 value）
      if (
        extractedData &&
        typeof extractedData === 'object' &&
        !Array.isArray(extractedData) &&
        ('xAxisData' in extractedData ||
          'seriesData' in extractedData ||
          'indicator' in extractedData ||
          'yAxisData' in extractedData ||
          ('value' in extractedData && 'max' in extractedData))
      ) {
        // 图表数据格式，直接合并到 props
        const mappedProps = { ...defaultProps, ...extractedData };
        // 如果有额外的字段映射，也应用
        if (dataSource.fieldMappings && dataSource.fieldMappings.length > 0) {
          return {
            data: extractedData,
            props: applyFieldMappings(
              extractedData,
              dataSource.fieldMappings,
              mappedProps,
            ),
          };
        }
        return { data: extractedData, props: mappedProps };
      }

      // 普通数据，应用字段映射
      const mappedProps = applyFieldMappings(
        extractedData,
        dataSource.fieldMappings,
        defaultProps,
      );

      return { data: extractedData, props: mappedProps };
    } catch (error) {
      console.error('Failed to fetch data source:', error);
      return { data: null, props: defaultProps };
    }
  }

  // API 类型
  if (dataSource.type === 'api' && dataSource.apiUrl) {
    try {
      const method = dataSource.apiMethod || 'GET';
      const params = dataSource.apiParams || {};
      const body = dataSource.apiBody || {};
      const headers = dataSource.apiHeaders || {};

      let response: any;

      response = await (method === 'GET'
        ? requestClient.get(dataSource.apiUrl, {
            params,
            headers,
          })
        : requestClient.post(dataSource.apiUrl, body, {
            params,
            headers,
          }));

      // 根据 dataPath 提取数据
      const extractedData = dataSource.dataPath
        ? getValueByPath(response, dataSource.dataPath)
        : response;

      // 应用字段映射
      const mappedProps = applyFieldMappings(
        extractedData,
        dataSource.fieldMappings,
        defaultProps,
      );

      return { data: extractedData, props: mappedProps };
    } catch (error) {
      console.error('Failed to fetch widget data:', error);
      return { data: null, props: defaultProps };
    }
  }

  return { data: null, props: defaultProps };
}

/**
 * 创建自动刷新定时器
 */
export function createRefreshTimer(
  dataSource: DataSourceConfig | undefined,
  callback: () => void,
): (() => void) | null {
  if (
    !dataSource?.refreshEnabled ||
    !dataSource.refreshInterval ||
    dataSource.refreshInterval <= 0
  ) {
    return null;
  }

  const timer = setInterval(callback, dataSource.refreshInterval * 1000);

  return () => clearInterval(timer);
}

/**
 * 获取组件支持的字段映射目标
 */
export function getWidgetFieldTargets(
  widgetType: string,
): { key: string; label: string }[] {
  const commonFields = [{ key: 'title', label: $t('dashboard-design.attribute.fieldLabels.title') }];

  const fieldMap: Record<string, { key: string; label: string }[]> = {
    'stat-card': [
      ...commonFields,
      { key: 'value', label: $t('dashboard-design.attribute.fieldLabels.value') },
      { key: 'trend', label: $t('dashboard-design.attribute.fieldLabels.trend') },
      { key: 'trendLabel', label: $t('dashboard-design.attribute.fieldLabels.trendLabel') },
      { key: 'prefix', label: $t('dashboard-design.attribute.fieldLabels.prefix') },
      { key: 'suffix', label: $t('dashboard-design.attribute.fieldLabels.suffix') },
    ],
    'progress-card': [...commonFields, { key: 'percentage', label: $t('dashboard-design.attribute.fieldLabels.percentage') }],
    'chart-line': [
      ...commonFields,
      { key: 'xAxisData', label: $t('dashboard-design.attribute.fieldLabels.xAxisData') },
      { key: 'seriesData', label: $t('dashboard-design.attribute.fieldLabels.seriesData') },
    ],
    'chart-bar': [
      ...commonFields,
      { key: 'xAxisData', label: $t('dashboard-design.attribute.fieldLabels.xAxisData') },
      { key: 'seriesData', label: $t('dashboard-design.attribute.fieldLabels.seriesData') },
    ],
    'chart-pie': [...commonFields, { key: 'seriesData', label: $t('dashboard-design.attribute.fieldLabels.seriesData') }],
    'chart-gauge': [
      ...commonFields,
      { key: 'value', label: $t('dashboard-design.attribute.fieldLabels.currentValue') },
      { key: 'min', label: $t('dashboard-design.attribute.fieldLabels.min') },
      { key: 'max', label: $t('dashboard-design.attribute.fieldLabels.max') },
    ],
    'todo-list': [...commonFields, { key: 'items', label: $t('dashboard-design.attribute.fieldLabels.listData') }],
    'notice-list': [...commonFields, { key: 'items', label: $t('dashboard-design.attribute.fieldLabels.listData') }],
    'ranking-list': [...commonFields, { key: 'items', label: $t('dashboard-design.attribute.fieldLabels.listData') }],
    'quick-links': [...commonFields, { key: 'links', label: $t('dashboard-design.attribute.fieldLabels.linkData') }],
  };

  return fieldMap[widgetType] || commonFields;
}
