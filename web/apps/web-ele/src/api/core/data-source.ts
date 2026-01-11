import { requestClient } from '#/api/request';

/**
 * 数据源类型定义
 */
export type DataSourceType = 'api' | 'sql' | 'static';
export type ResultType =
  | 'chart-axis'
  | 'chart-gauge'
  | 'chart-heatmap'
  | 'chart-pie'
  | 'chart-radar'
  | 'chart-scatter'
  | 'list'
  | 'object'
  | 'tree'
  | 'value';
export type HttpMethod = 'GET' | 'POST';

/**
 * 参数定义
 */
export interface ParamDefinition {
  name: string;
  label?: string;
  type?: 'boolean' | 'float' | 'integer' | 'string';
  required?: boolean;
  default?: any;
}

/**
 * 树形配置
 */
export interface TreeConfig {
  id_field?: string;
  parent_field?: string;
  children_field?: string;
  root_value?: any;
}

/**
 * 图表配置
 */
export interface ChartConfig {
  // chart-axis（轴向图表）配置
  x_field?: string; // X轴字段
  series_fields?: string[]; // 系列字段（多个）
  series_names?: string[]; // 系列名称（可选）
  // chart-pie（饼图）配置
  name_field?: string; // 名称字段
  value_field?: string; // 数值字段
  // chart-gauge（仪表盘）配置
  max_field?: string; // 最大值字段
  // chart-radar（雷达图）配置
  indicator_field?: string; // 指标名称字段
  value_fields?: string[]; // 数值字段（多个系列）
  // chart-scatter（散点图）配置
  y_field?: string; // Y坐标字段
  size_field?: string; // 大小字段（气泡图）
}

/**
 * 数据源完整类型
 */
export interface DataSource {
  id: string;
  name: string;
  code: string;
  source_type: DataSourceType;
  description?: string;
  status: boolean;
  sort?: number;
  // API 配置
  api_url?: string;
  api_method?: HttpMethod;
  api_headers?: Record<string, string>;
  api_body?: Record<string, any>;
  api_timeout?: number;
  api_data_path?: string;
  // SQL 配置
  sql_content?: string;
  db_connection?: string;
  // 静态数据
  static_data?: any[];
  // 参数定义
  params?: ParamDefinition[];
  // 结果处理
  result_type?: ResultType;
  tree_config?: TreeConfig;
  field_mapping?: Record<string, string>;
  chart_config?: ChartConfig;
  // 缓存配置
  cache_enabled?: boolean;
  cache_ttl?: number;
  // 系统字段
  sys_create_datetime?: string;
  sys_update_datetime?: string;
}

/**
 * 数据源简单类型（用于下拉选择）
 */
export interface DataSourceSimple {
  id: string;
  name: string;
  code: string;
  source_type: DataSourceType;
  result_type?: ResultType;
  description?: string;
}

/**
 * 创建/更新数据源输入
 */
export interface DataSourceInput {
  name: string;
  code: string;
  source_type: DataSourceType;
  description?: string;
  status?: boolean;
  sort?: number;
  // API 配置
  api_url?: string;
  api_method?: HttpMethod;
  api_headers?: Record<string, string>;
  api_body?: Record<string, any>;
  api_timeout?: number;
  api_data_path?: string;
  // SQL 配置
  sql_content?: string;
  db_connection?: string;
  // 静态数据
  static_data?: any[];
  // 参数定义
  params?: ParamDefinition[];
  // 结果处理
  result_type?: ResultType;
  tree_config?: TreeConfig;
  field_mapping?: Record<string, string>;
  chart_config?: ChartConfig;
  // 缓存配置
  cache_enabled?: boolean;
  cache_ttl?: number;
}

/**
 * 列表查询参数
 */
export interface DataSourceListParams {
  page?: number;
  pageSize?: number;
  name?: string;
  code?: string;
  source_type?: DataSourceType;
  status?: boolean;
}

/**
 * 分页响应
 */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
}

/**
 * 预览请求
 */
export interface PreviewRequest {
  params?: Record<string, any>;
  limit?: number;
}

/**
 * 测试请求
 */
export interface TestRequest {
  source_type: DataSourceType;
  // API 配置
  api_url?: string;
  api_method?: HttpMethod;
  api_headers?: Record<string, string>;
  api_body?: Record<string, any>;
  api_timeout?: number;
  api_data_path?: string;
  // SQL 配置
  sql_content?: string;
  db_connection?: string;
  // 静态数据
  static_data?: any[];
  // 参数
  params_def?: ParamDefinition[];
  params?: Record<string, any>;
  // 结果处理
  result_type?: ResultType;
  tree_config?: TreeConfig;
  field_mapping?: Record<string, string>;
  chart_config?: ChartConfig;
}

/**
 * 复制请求
 */
export interface CopyRequest {
  new_code: string;
  new_name?: string;
}

// ============ CRUD API ============

/**
 * 创建数据源
 */
export async function createDataSourceApi(data: DataSourceInput) {
  return requestClient.post<DataSource>('/api/core/data-source', data);
}

/**
 * 获取数据源列表（分页）
 */
export async function getDataSourceListApi(params?: DataSourceListParams) {
  return requestClient.get<PaginatedResponse<DataSource>>(
    '/api/core/data-source',
    {
      params,
    },
  );
}

/**
 * 获取所有数据源（不分页）
 */
export async function getAllDataSourceApi() {
  return requestClient.get<DataSourceSimple[]>('/api/core/data-source/get/all');
}

/**
 * 获取数据源详情
 */
export async function getDataSourceDetailApi(id: string) {
  return requestClient.get<DataSource>(`/api/core/data-source/${id}`);
}

/**
 * 更新数据源
 */
export async function updateDataSourceApi(id: string, data: DataSourceInput) {
  return requestClient.put<DataSource>(`/api/core/data-source/${id}`, data);
}

/**
 * 删除数据源
 */
export async function deleteDataSourceApi(id: string) {
  return requestClient.delete<DataSource>(`/api/core/data-source/${id}`);
}

// ============ 执行 API ============

/**
 * 执行数据源（GET 方式）
 */
export async function executeDataSourceGetApi(
  code: string,
  params?: Record<string, any>,
) {
  return requestClient.get<any>(`/api/core/data-source/execute/${code}`, {
    params,
  });
}

/**
 * 执行数据源（POST 方式）
 */
export async function executeDataSourcePostApi(
  code: string,
  params?: Record<string, any>,
) {
  return requestClient.post<any>(`/api/core/data-source/execute/${code}`, {
    params: params || {},
  });
}

/**
 * 预览数据源数据
 */
export async function previewDataSourceApi(id: string, data?: PreviewRequest) {
  return requestClient.post<{ data: any[]; limited: number; total: number }>(
    `/api/core/data-source/${id}/preview`,
    data || { params: {}, limit: 100 },
  );
}

/**
 * 测试数据源配置
 */
export async function testDataSourceApi(data: TestRequest) {
  return requestClient.post<{
    data: any[];
    limited: number;
    success: boolean;
    total: number;
  }>('/api/core/data-source/test', data);
}

// ============ 其他 API ============

/**
 * 复制数据源
 */
export async function copyDataSourceApi(id: string, data: CopyRequest) {
  return requestClient.post<DataSource>(
    `/api/core/data-source/${id}/copy`,
    data,
  );
}

/**
 * 清除数据源缓存
 */
export async function clearDataSourceCacheApi(id: string) {
  return requestClient.post<{ msg: string }>(
    `/api/core/data-source/${id}/clear-cache`,
  );
}

/**
 * 检查编码是否可用
 */
export async function checkCodeAvailableApi(code: string) {
  return requestClient.get<{ available: boolean }>(
    `/api/core/data-source/check-code/${code}`,
  );
}
