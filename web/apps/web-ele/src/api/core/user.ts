import type { UserInfo } from '@vben/types';

import { requestClient } from '#/api/request';

/**
 * 用户相关类型定义
 */
export interface User {
  id: string;
  username: string;
  email?: string;
  mobile?: string;
  avatar?: string; // UUID string
  name?: string;
  gender?: number;
  user_type?: number;
  user_status?: number;
  birthday?: string;
  city?: string;
  address?: string;
  bio?: string;
  dept_id?: string; // UUID string
  dept_name?: string;
  manager_id?: string; // UUID string
  manager_name?: string;
  user_type_display?: string;
  user_status_display?: string;
  gender_display?: string;
  role_names?: string[];
  post_names?: string[];
  sys_create_datetime?: string;
  sys_update_datetime?: string;
  is_active: number;
}

export interface UserCreateInput {
  username: string;
  email?: string;
  mobile?: string;
  avatar?: string;
  name?: string;
  gender?: number;
  user_type?: number;
  user_status?: number;
  birthday?: string;
  city?: string;
  address?: string;
  bio?: string;
  dept_id?: string;
  manager_id?: string;
  post?: string[];
  core_roles?: string[];
}

export interface UserUpdateInput extends Partial<UserCreateInput> {}

export interface UserPasswordResetInput {
  new_password: string;
  confirm_password: string;
}

export interface UserChangePasswordInput {
  old_password: string;
  new_password: string;
  confirm_password: string;
}

export interface UserProfileUpdateInput {
  name?: string;
  email?: string;
  mobile?: string;
  avatar?: string;
  gender?: number;
  birthday?: string;
  city?: string;
  address?: string;
  bio?: string;
}

export interface UserBatchDeleteInput {
  ids: string[];
}

export interface UserBatchUpdateStatusInput {
  ids: string[];
  user_status: number;
}

export interface UserPermissionCheckInput {
  permission_code: string;
}

export interface UserListParams {
  page?: number;
  pageSize?: number;
  name?: string;
  username?: string;
  user_status?: number;
  user_type?: number;
  dept_ids?: string[];
  mobile?: string;
  email?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
}

/**
 * 获取用户信息
 */
export async function getUserInfoApi() {
  return requestClient.get<UserInfo>('/api/core/userinfo');
}

/**
 * 创建用户
 */
export async function createUserApi(data: UserCreateInput) {
  return requestClient.post<User>('/api/core/user', data);
}

/**
 * 获取用户列表（分页）
 */
export async function getUserListApi(params?: UserListParams) {
  return requestClient.get<PaginatedResponse<User>>('/api/core/user', {
    params,
  });
}

/**
 * 获取用户详情
 */
export async function getUserDetailApi(userId: string) {
  return requestClient.get<User>(`/api/core/user/${userId}`);
}

/**
 * 更新用户
 */
export async function updateUserApi(userId: string, data: UserUpdateInput) {
  return requestClient.put<User>(`/api/core/user/${userId}`, data);
}

/**
 * 删除用户
 */
export async function deleteUserApi(userId: string) {
  return requestClient.delete<User>(`/api/core/user/${userId}`);
}

/**
 * 批量删除用户
 */
export async function batchDeleteUserApi(data: UserBatchDeleteInput) {
  return requestClient.post<{ count: number }>(
    '/api/core/user/batch_delete',
    data,
  );
}

/**
 * 批量更新用户状态
 */
export async function batchUpdateUserStatusApi(
  data: UserBatchUpdateStatusInput,
) {
  return requestClient.post<{ count: number }>(
    '/api/core/user/batch_update_status',
    data,
  );
}

/**
 * 重置用户密码
 */
export async function resetUserPasswordApi(
  userId: string,
  data: UserPasswordResetInput,
) {
  return requestClient.post<User>(
    `/api/core/user/reset/password/${userId}`,
    data,
  );
}

/**
 * 更新用户个人信息
 */
export async function updateUserProfileApi(data: UserProfileUpdateInput) {
  return requestClient.put<User>('/api/core/user/profile', data);
}

/**
 * 检查用户权限
 */
export async function checkUserPermissionApi(data: UserPermissionCheckInput) {
  return requestClient.post<{ has_permission: boolean }>(
    '/api/core/user/check_permission',
    data,
  );
}

/**
 * 获取用户下属列表
 */
export async function getUserSubordinatesApi(userId: string) {
  return requestClient.get<User[]>(`/api/core/user/${userId}/subordinates`);
}

/**
 * 获取简单用户列表（用于选择器）
 */
export async function getSimpleUserListApi() {
  return requestClient.get<User[]>('/api/core/user/simple');
}

/**
 * 获取当前用户个人信息
 */
export async function getCurrentUserProfileApi() {
  return requestClient.get<User>('/api/core/user/profile/me');
}

/**
 * 部分更新用户个人信息
 */
export async function patchUserProfileApi(data: UserProfileUpdateInput) {
  return requestClient.patch<User>('/api/core/user/profile', data);
}

/**
 * 修改密码
 */
export async function changePasswordApi(data: UserChangePasswordInput) {
  return requestClient.post<{ message: string }>(
    '/api/core/user/change-password',
    data,
  );
}
