import { requestClient } from '#/api/request';

/**
 * 页面管理 API
 * 页面元数据的 CRUD、发布、复制、导入导出
 */

// ============ 类型定义 ============

/** 页面元数据 */
export interface PageMeta {
  id: string;
  application_id?: string;
  name: string;
  code: string;
  category: string;
  description: string;
  status: string;
  version: number;
  page_config: Record<string, any>;
  sort: number;
  sys_create_datetime: string;
  sys_update_datetime: string;
}

/** 页面列表项 */
export interface PageMetaListItem {
  id: string;
  application_id?: string;
  name: string;
  code: string;
  category: string;
  description: string;
  status: string;
  version: number;
  sort: number;
  sys_create_datetime: string;
  sys_update_datetime: string;
}

/** 创建页面请求 */
export interface PageMetaCreateInput {
  application_id?: string;
  name: string;
  code: string;
  category?: string;
  description?: string;
  sort?: number;
  page_config?: Record<string, any>;
}

/** 更新页面请求 */
export interface PageMetaUpdateInput {
  name?: string;
  category?: string;
  description?: string;
  sort?: number;
  page_config?: Record<string, any>;
}

/** 导入页面请求 */
export interface PageImportInput {
  name: string;
  code: string;
  category?: string;
  description?: string;
  page_config?: Record<string, any>;
}

/** 列表查询参数 */
export interface PageListParams {
  page?: number;
  pageSize?: number;
  applicationId?: string;
  name?: string;
  code?: string;
  category?: string;
  status?: string;
}

/** 发布配置 */
export interface PagePublishInput {
  /** 菜单名称 */
  menu_name: string;
  /** 上级菜单ID */
  menu_parent_id?: string;
  /** 菜单图标 */
  menu_icon?: string;
  /** 菜单排序 */
  menu_order?: number;
}

/** 分页响应 */
interface PagePaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
}

// ============ 页面元数据 API ============

/**
 * 获取页面列表（分页）
 */
export async function getPageListApi(params?: PageListParams) {
  return requestClient.get<PagePaginatedResponse<PageMetaListItem>>(
    '/api/core/page/list',
    { params },
  );
}

/**
 * 获取分类列表
 */
export async function getPageCategoriesApi() {
  return requestClient.get<string[]>('/api/core/page/categories');
}

/**
 * 获取页面详情
 */
export async function getPageDetailApi(pageId: string) {
  return requestClient.get<PageMeta>(`/api/core/page/${pageId}`);
}

/**
 * 根据编码获取页面
 */
export async function getPageByCodeApi(code: string) {
  return requestClient.get<PageMeta>(`/api/core/page/code/${code}`);
}

/**
 * 创建页面
 */
export async function createPageApi(data: PageMetaCreateInput) {
  return requestClient.post<PageMeta>('/api/core/page', data);
}

/**
 * 更新页面
 */
export async function updatePageApi(pageId: string, data: PageMetaUpdateInput) {
  return requestClient.put<PageMeta>(`/api/core/page/${pageId}`, data);
}

/**
 * 删除页面
 */
export async function deletePageApi(pageId: string) {
  return requestClient.delete<PageMeta>(`/api/core/page/${pageId}`);
}

/**
 * 批量删除页面
 */
export async function batchDeletePageApi(ids: string[]) {
  return requestClient.delete<{ count: number }>('/api/core/page/batch', {
    params: { ids },
  });
}

/**
 * 发布页面
 */
export async function publishPageApi(pageId: string, data: PagePublishInput) {
  return requestClient.post<PageMeta>(`/api/core/page/${pageId}/publish`, data);
}

/**
 * 取消发布页面
 */
export async function unpublishPageApi(pageId: string) {
  return requestClient.post<PageMeta>(`/api/core/page/${pageId}/unpublish`);
}

/**
 * 复制页面
 */
export async function copyPageApi(
  pageId: string,
  newCode: string,
  newName?: string,
) {
  return requestClient.post<PageMeta>(`/api/core/page/${pageId}/copy`, null, {
    params: { new_code: newCode, new_name: newName },
  });
}

/**
 * 导出页面配置（返回 JSON 文件）
 */
export async function exportPageConfigApi(pageId: string) {
  return requestClient.get<Blob>(`/api/core/page/${pageId}/export`, {
    responseType: 'blob',
  });
}

/**
 * 导入页面配置
 */
export async function importPageConfigApi(data: PageImportInput) {
  return requestClient.post<PageMeta>('/api/core/page/import', data);
}
