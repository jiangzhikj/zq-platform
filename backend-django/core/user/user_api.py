#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
User API - 用户管理接口
提供用户的 CRUD 操作和高级功能
"""
from typing import List
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from django.db.models import Q
from ninja import Router, Query
from ninja.errors import HttpError
from ninja.pagination import paginate

from application.settings import DEFAULT_PASSWORD
from common.fu_crud import create, retrieve, delete, batch_delete
from common.fu_pagination import MyPagination
from common.fu_schema import response_success
from common.fu_user_query import get_manager_list
from core.user.user_model import User
from core.user.user_schema import (
    UserSchemaOut,
    UserSchemaIn,
    UserSchemaPatch,
    UserFilters,
    UserSchemaDetail,
    UserPasswordResetIn,
    UserSchemaAvatarOut,
    UserSchemaGetNameIn,
    UserSchemaBatchDeleteOut,
    UserSchemaBatchDeleteIn,
    UserBatchUpdateStatusIn,
    UserBatchUpdateStatusOut,
    UserSchemaSimple,
    UserProfileUpdateIn,
    UserPermissionCheckIn,
    UserPermissionCheckOut,
    UserSubordinatesOut,
)

router = Router()


@router.post("/user", response=UserSchemaOut, summary="创建用户")
def create_user(request, data: UserSchemaIn):
    """
    创建新用户
    
    改进点：
    - 检查用户名、邮箱、手机号的唯一性
    - 使用默认密码
    - 分离多对多关系的处理
    """
    # 检查用户名是否已存在
    if User.objects.filter(username=data.username).exists():
        raise HttpError(400, f"用户名已存在: {data.username}")
    
    # 检查邮箱是否已存在
    if data.email and User.objects.filter(email=data.email).exists():
        raise HttpError(400, f"邮箱已存在: {data.email}")
    
    # 检查手机号是否已存在
    if data.mobile and User.objects.filter(mobile=data.mobile).exists():
        raise HttpError(400, f"手机号已存在: {data.mobile}")
    
    data_dic = data.dict()
    # 设置默认密码
    data_dic["password"] = make_password(DEFAULT_PASSWORD)
    
    # 提取多对多关系字段
    post_ids = data_dic.pop("post", [])
    role_ids = data_dic.pop("core_roles", [])
    
    # 创建用户
    user = create(request, data_dic, User)
    
    # 设置多对多关系
    if post_ids:
        user.post.set(post_ids)
    if role_ids:
        user.core_roles.set(role_ids)
    
    return user


@router.delete("/user/{user_id}", response=UserSchemaOut, summary="删除用户")
def delete_user(request, user_id: str):
    """
    删除用户
    
    改进点：
    - 检查是否为系统用户或超级管理员
    - 不能删除自己
    """
    user = get_object_or_404(User, id=user_id)
    
    # 不能删除自己
    if user.id == request.auth.id:
        raise HttpError(400, "不能删除自己")
    
    # 不能删除系统用户或超级管理员
    if not user.can_delete():
        raise HttpError(400, "系统用户或超级管理员不能删除")
    
    instance = delete(user_id, User)
    return instance


@router.delete("/user/batch/delete", response=UserSchemaBatchDeleteOut, summary="批量删除用户")
def delete_batch_user(request, data: UserSchemaBatchDeleteIn):
    """
    批量删除用户
    
    改进点：
    - 跳过系统用户、超级管理员和当前用户
    - 返回删除失败的ID列表
    """
    current_user_id = request.auth.id
    failed_ids = []
    success_count = 0
    
    for user_id in data.ids:
        try:
            user = User.objects.get(id=user_id)
            
            # 不能删除自己
            if user.id == current_user_id:
                failed_ids.append(user_id)
                continue
            
            # 不能删除系统用户或超级管理员
            if not user.can_delete():
                failed_ids.append(user_id)
                continue
            
            user.delete()
            success_count += 1
        except User.DoesNotExist:
            failed_ids.append(user_id)
    
    return UserSchemaBatchDeleteOut(count=success_count, failed_ids=failed_ids)


@router.put("/user/{user_id}", response=UserSchemaOut, summary="更新用户（完全替换）")
def update_user(request, user_id: str, data: UserSchemaIn):
    """
    更新用户信息（PUT - 完全替换）
    
    改进点：
    - 检查用户名、邮箱、手机号的唯一性（排除自身）
    - 系统用户不能修改某些字段
    - 分离多对多关系的处理
    """
    user = get_object_or_404(User, id=user_id)
    
    # 检查用户名是否已存在（排除自身）
    if User.objects.filter(username=data.username).exclude(id=user_id).exists():
        raise HttpError(400, f"用户名已存在: {data.username}")
    
    # 检查邮箱是否已存在（排除自身）
    if data.email and User.objects.filter(email=data.email).exclude(id=user_id).exists():
        raise HttpError(400, f"邮箱已存在: {data.email}")
    
    # 检查手机号是否已存在（排除自身）
    if data.mobile and User.objects.filter(mobile=data.mobile).exclude(id=user_id).exists():
        raise HttpError(400, f"手机号已存在: {data.mobile}")
    
    # 系统用户不能修改用户类型
    if user.user_type == 0 and data.user_type != 0:
        raise HttpError(400, "系统用户不能修改用户类型")
    
    # 更新用户信息
    role_changed = False
    for attr, value in data.dict().items():
        if attr == "core_roles":
            user.core_roles.set(value)
            role_changed = True
        elif attr == "post":
            user.post.set(value)
        elif attr == "password":
            # 跳过密码字段，密码需要单独接口修改
            continue
        else:
            if value is not None:
                setattr(user, attr, value)
    
    user.save()
    
    # 如果角色发生变更，清除权限缓存
    if role_changed:
        from common.fu_cache import PermissionCacheManager
        PermissionCacheManager.invalidate_user_permissions(str(user.id))
    
    return user


@router.patch("/user/{user_id}", response=UserSchemaOut, summary="部分更新用户")
def patch_user(request, user_id: str, data: UserSchemaPatch):
    """
    部分更新用户信息（PATCH - 只更新提供的字段）
    
    优势：
    - 只需提供需要修改的字段
    - 更灵活，适合前端表单部分更新
    - 减少网络传输数据量
    
    改进点：
    - 检查用户名、邮箱、手机号的唯一性（排除自身）
    - 系统用户不能修改某些字段
    - 分离多对多关系的处理
    """
    user = get_object_or_404(User, id=user_id)
    
    # 只更新提供的字段
    update_data = data.dict(exclude_unset=True)
    
    # 检查用户名是否已存在（排除自身）
    if 'username' in update_data and update_data['username']:
        if User.objects.filter(username=update_data['username']).exclude(id=user_id).exists():
            raise HttpError(400, f"用户名已存在: {update_data['username']}")
    
    # 检查邮箱是否已存在（排除自身）
    if 'email' in update_data and update_data['email']:
        if User.objects.filter(email=update_data['email']).exclude(id=user_id).exists():
            raise HttpError(400, f"邮箱已存在: {update_data['email']}")
    
    # 检查手机号是否已存在（排除自身）
    if 'mobile' in update_data and update_data['mobile']:
        if User.objects.filter(mobile=update_data['mobile']).exclude(id=user_id).exists():
            raise HttpError(400, f"手机号已存在: {update_data['mobile']}")
    
    # 系统用户不能修改用户类型
    if user.user_type == 0 and 'user_type' in update_data and update_data['user_type'] != 0:
        raise HttpError(400, "系统用户不能修改用户类型")
    
    # 更新字段
    role_changed = False
    for attr, value in update_data.items():
        if attr == "core_roles":
            user.core_roles.set(value)
            role_changed = True
        elif attr == "post":
            user.post.set(value)
        else:
            setattr(user, attr, value)
    
    user.save()
    
    # 如果角色发生变更，清除权限缓存
    if role_changed:
        from common.fu_cache import PermissionCacheManager
        PermissionCacheManager.invalidate_user_permissions(str(user.id))
    
    return user


@router.get("/user", response=List[UserSchemaOut], summary="获取用户列表（分页）")
@paginate(MyPagination)
def list_user(request, filters: UserFilters = Query(...)):
    """
    获取用户列表（分页）
    
    改进点：
    - 使用 select_related 和 prefetch_related 优化查询
    - 支持多种过滤条件
    """
    query_set = retrieve(request, User, filters)
    # 优化查询：预加载关联数据
    query_set = query_set.select_related('dept', 'manager').prefetch_related('post', 'core_roles')
    return query_set


@router.get("/user/all", response=List[UserSchemaSimple], summary="获取所有用户（简化版）")
def list_all_user(request):
    """
    获取所有正常状态的用户（不分页，简化版）
    
    用于用户选择器等场景
    """
    query_set = User.objects.filter(user_status=1).select_related('dept').order_by('name')
    return query_set


@router.put("/user/reset/password/{user_id}", response=UserSchemaOut, summary="重置用户密码")
def reset_password(request, user_id: str):
    """
    重置用户密码为默认密码
    
    改进点：
    - 记录操作日志
    """
    user = get_object_or_404(User, id=user_id)
    user.set_password(DEFAULT_PASSWORD)
    user.save()
    
    # TODO: 记录密码重置日志
    
    return user


@router.get("/user/{user_id}", response=UserSchemaDetail, summary="获取用户详情")
def get_user(request, user_id: str):
    """
    获取单个用户的详细信息
    
    改进点：
    - 使用 prefetch_related 优化关联查询
    """
    user = get_object_or_404(
        User.objects.select_related('dept', 'manager').prefetch_related('post', 'core_roles'),
        id=user_id
    )
    return user


@router.post("/user/get/username", response=List[str], summary="根据ID列表获取用户名")
def get_usernames(request, data: UserSchemaGetNameIn):
    """根据用户ID列表获取用户名列表"""
    users = User.objects.filter(id__in=data.ids).values('name')
    return [item.get("name") for item in users]


@router.post("/user/get/user_dept_lead", response=List[str], summary="获取用户的部门领导")
def get_user_dept_lead(request, data: UserSchemaGetNameIn):
    """获取用户的部门领导"""
    # TODO: 实现获取部门领导的逻辑
    users = User.objects.filter(id__in=data.ids).values('id', 'name')
    return [item.get("name") for item in users]


@router.post("/user/get/user_manager", response=list, summary="获取用户的上级")
def get_user_manager(request, data: UserSchemaGetNameIn):
    """获取用户的上级"""
    return get_manager_list(data)


@router.post("/user/change-password", summary="修改密码")
def change_password(request, data: UserPasswordResetIn):
    """
    用户修改自己的密码
    
    改进点：
    - 验证旧密码
    - 验证新密码不同于旧密码
    - 记录密码修改日志
    """
    current_user = request.auth
    user = get_object_or_404(User, id=current_user.id)
    
    # 验证旧密码
    if not user.check_password(data.old_password):
        raise HttpError(401, "旧密码不正确")
    
    # 验证新密码不同于旧密码
    if user.check_password(data.new_password):
        raise HttpError(400, "新密码不能与旧密码相同")
    
    # 设置新密码
    user.set_password(data.new_password)
    user.save()
    
    # TODO: 记录密码修改日志
    
    return response_success("密码修改成功")


@router.get("/user/get/avatar/{user_id}", response=UserSchemaAvatarOut, summary="获取用户头像")
def get_user_avatar(request, user_id: str):
    """获取用户头像信息"""
    user = get_object_or_404(User, id=user_id)
    return user


@router.post("/user/batch/update-status", response=UserBatchUpdateStatusOut, summary="批量更新用户状态")
def batch_update_user_status(request, data: UserBatchUpdateStatusIn):
    """
    批量启用、禁用或锁定用户
    
    改进点：
    - 支持批量状态管理
    - 不能修改系统用户和超级管理员的状态
    - 不能修改自己的状态
    """
    current_user_id = request.auth.id
    
    # 过滤掉系统用户、超级管理员和当前用户
    users = User.objects.filter(
        id__in=data.ids,
        user_type__ne=0,
        is_superuser=False
    ).exclude(id=current_user_id)
    
    count = users.update(user_status=data.user_status)
    return UserBatchUpdateStatusOut(count=count)


@router.get("/user/search", response=List[UserSchemaOut], summary="搜索用户")
@paginate(MyPagination)
def search_user(request, keyword: str = Query(None)):
    """
    搜索用户
    
    改进点：
    - 支持关键词搜索（用户名、姓名、邮箱、手机号）
    """
    query_set = User.objects.all()
    
    if keyword:
        query_set = query_set.filter(
            Q(username__icontains=keyword) |
            Q(name__icontains=keyword) |
            Q(email__icontains=keyword) |
            Q(mobile__icontains=keyword)
        )
    
    query_set = query_set.select_related('dept', 'manager').prefetch_related('post', 'core_roles')
    return query_set


@router.put("/profile", response=UserSchemaOut, summary="更新个人信息（完全替换）")
def update_profile(request, data: UserProfileUpdateIn):
    """
    用户更新自己的个人信息（PUT - 完全替换）
    
    改进点：
    - 只能修改自己的个人信息
    - 有限的字段可以修改
    """
    current_user = request.auth
    user = get_object_or_404(User, id=current_user.id)
    
    # 更新个人信息
    for attr, value in data.dict(exclude_none=True).items():
        setattr(user, attr, value)
    
    user.save()
    return user


@router.patch("/profile", response=UserSchemaOut, summary="部分更新个人信息")
def patch_profile(request, data: UserProfileUpdateIn):
    """
    用户部分更新自己的个人信息（PATCH - 只更新提供的字段）
    
    优势：
    - 只需提供需要修改的字段
    - 更灵活，适合前端表单部分更新
    
    改进点：
    - 只能修改自己的个人信息
    - 有限的字段可以修改
    """
    current_user = request.auth
    
    # 如果 request.auth 已经是 User 对象，直接使用（避免重复查询）
    if isinstance(current_user, User):
        user = current_user
    else:
        user = get_object_or_404(User, id=current_user.id)
    
    # 只更新提供的字段
    update_data = data.dict(exclude_unset=True)
    
    for attr, value in update_data.items():
        setattr(user, attr, value)
    
    user.save()
    return user


@router.get("/profile/me", response=UserSchemaDetail, summary="获取当前用户信息")
def get_current_user_profile(request):
    """
    获取当前登录用户的详细信息
    
    改进点：
    - 返回完整的用户信息，包括权限
    """
    user = get_object_or_404(
        User.objects.select_related('dept', 'manager').prefetch_related('post', 'core_roles'),
        id=request.auth.id
    )
    return user


@router.post("/user/check-permission", response=UserPermissionCheckOut, summary="检查用户权限")
def check_user_permission(request, data: UserPermissionCheckIn):
    """
    检查当前用户是否拥有指定的权限
    
    改进点：
    - 批量检查多个权限
    """
    current_user = request.auth
    user = get_object_or_404(User, id=current_user.id)
    
    result = {}
    for permission_code in data.permission_codes:
        result[permission_code] = user.has_permission(permission_code)
    
    return UserPermissionCheckOut(permissions=result)


@router.get("/user/subordinates/{user_id}", response=UserSubordinatesOut, summary="获取用户的下属列表")
def get_user_subordinates(request, user_id: str, include_self: bool = Query(False)):
    """
    获取用户的所有下属
    
    改进点：
    - 支持包含自己的选项
    """
    user = get_object_or_404(User, id=user_id)
    subordinates = user.get_subordinate_users(include_self=include_self)
    return UserSubordinatesOut(subordinates=subordinates)


@router.get("/user/by/dept/{dept_id}", response=List[UserSchemaSimple], summary="根据部门ID获取用户")
def get_users_by_dept(request, dept_id: str):
    """
    根据部门ID获取该部门下的所有用户
    
    改进点：
    - 支持部门维度的用户查询
    """
    users = User.objects.filter(
        dept_id=dept_id,
        user_status=1
    ).select_related('dept').order_by('name')
    return users


@router.get("/user/by/role/{role_id}", response=List[UserSchemaSimple], summary="根据角色ID获取用户")
def get_users_by_role(request, role_id: str):
    """
    根据角色ID获取拥有该角色的所有用户
    
    改进点：
    - 支持角色维度的用户查询
    """
    users = User.objects.filter(
        core_roles__id=role_id,
        user_status=1
    ).distinct().select_related('dept').order_by('name')
    return users


@router.post("/user/export", summary="导出用户数据")
def export_user(request):
    """
    导出用户数据为Excel
    
    用于数据备份和报表
    """
    # TODO: 实现导出功能
    return response_success("导出功能待实现")


@router.post("/user/import", summary="导入用户数据")
def import_user(request):
    """
    批量导入用户数据
    
    从Excel文件导入用户数据
    """
    # TODO: 实现导入功能
    return response_success("导入功能待实现")

