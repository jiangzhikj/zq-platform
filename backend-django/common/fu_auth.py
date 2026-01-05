#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author: 臧成龙
@Contact: 939589097@qq.com
@Time: 2025-12-31
@File: fu_auth.py
@Desc: JWT 鉴权和权限校验 - 基于 Core 模块的权限结构重新设计
"""
"""
JWT 鉴权和权限校验
基于 Core 模块的权限结构重新设计
"""
import logging
import re
from calendar import timegm
from datetime import timedelta, datetime, timezone

import jwt
from django.core.cache import cache
from ninja.errors import HttpError
from ninja.security import HttpBearer, APIKeyQuery

from application import settings
from application.settings import API_WHITE_LIST
from env import IS_DEMO

from django.urls import resolve, Resolver404

logger = logging.getLogger(__name__)


# ===================== 登录防暴力破解 =====================
class LoginAttemptProtection:
    """
    登录尝试保护机制，防止暴力破解
    """
    FAILED_ATTEMPT_KEY = "login_attempt_{}"  # username 或 ip
    FAILED_ATTEMPT_LIMIT = 15  # 最多15次失败
    FAILED_ATTEMPT_TIMEOUT = 5 * 60  # 5分钟内
    IP_LOCKOUT_KEY = "login_lockout_ip_{}"
    IP_LOCKOUT_DURATION = 15 * 60  # IP锁定15分钟

    @classmethod
    def check_login_attempt(cls, username: str, ip_address: str) -> tuple[bool, str]:
        """
        检查登录尝试是否超过限制
        
        返回: (is_allowed, message)
        """
        # 检查IP是否被锁定
        ip_lockout_key = cls.IP_LOCKOUT_KEY.format(ip_address)
        if cache.get(ip_lockout_key):
            return False, "登录尝试过多，请稍后再试"

        # 检查用户名失败次数
        attempt_key = cls.FAILED_ATTEMPT_KEY.format(f"user_{username}")
        attempts = cache.get(attempt_key, 0)

        if attempts >= cls.FAILED_ATTEMPT_LIMIT:
            # 锁定IP
            cache.set(ip_lockout_key, True, cls.IP_LOCKOUT_DURATION)
            return False, "登录尝试过多，请稍后再试"

        return True, ""

    @classmethod
    def record_login_failure(cls, username: str, ip_address: str):
        """记录登录失败"""
        attempt_key = cls.FAILED_ATTEMPT_KEY.format(f"user_{username}")
        attempts = cache.get(attempt_key, 0)
        cache.set(attempt_key, attempts + 1, cls.FAILED_ATTEMPT_TIMEOUT)
        logger.warning(f"登录失败记录: {username} from {ip_address}, 尝试次数: {attempts + 1}")

    @classmethod
    def record_login_success(cls, username: str):
        """记录登录成功，清除失败计数"""
        attempt_key = cls.FAILED_ATTEMPT_KEY.format(f"user_{username}")
        cache.delete(attempt_key)


# ===================== Token 黑名单管理 =====================
class TokenBlacklist:
    """
    Token 黑名单管理，用于登出和密码修改后撤销 token
    """
    BLACKLIST_KEY = "token_blacklist_{}"

    @classmethod
    def add_to_blacklist(cls, token: str, user_id: str, exp_time: int):
        """
        将 token 加入黑名单
        
        :param token: JWT token
        :param user_id: 用户ID
        :param exp_time: token过期时间戳
        """
        key = cls.BLACKLIST_KEY.format(user_id)
        blacklist = cache.get(key, {})

        # 计算剩余有效期
        remaining_time = exp_time - int(datetime.now(timezone.utc).timestamp())
        if remaining_time > 0:
            blacklist[token] = exp_time
            cache.set(key, blacklist, remaining_time)
            logger.info(f"令牌已加入黑名单: 用户 {user_id}")

    @classmethod
    def is_blacklisted(cls, token: str, user_id: str) -> bool:
        """检查 token 是否在黑名单中"""
        key = cls.BLACKLIST_KEY.format(user_id)
        blacklist = cache.get(key, {})
        return token in blacklist

    @classmethod
    def revoke_user_tokens(cls, user_id: str):
        """撤销用户的所有 token"""
        key = cls.BLACKLIST_KEY.format(user_id)
        cache.delete(key)
        logger.info(f"已撤销用户 {user_id} 的所有令牌")


# HTTP 方法映射
HTTP_METHOD_MAP = {
    'GET': 0,
    'POST': 1,
    'PUT': 2,
    'DELETE': 3,
    'PATCH': 4,
}


def is_in_white_list(path: str, white_apis: list) -> bool:
    """
    检查路径是否在白名单中，支持通配符 *

    参数:
        path: 需要检查的路径
        white_apis: 包含通配符的白名单列表

    返回:
        如果路径匹配白名单中的任何模式，返回True，否则返回False
    """
    for api in white_apis:
        # 精确匹配
        if '*' not in api:
            if path == api:
                return True
        else:
            # 通配符匹配
            if api.endswith('*') and not api.startswith('*'):
                # 前缀匹配：/api/core/*
                prefix = api[:-1]
                if path.startswith(prefix):
                    return True
            elif api.startswith('*') and not api.endswith('*'):
                # 后缀匹配：*/login
                suffix = api[1:]
                if path.endswith(suffix):
                    return True
            elif '*' in api:
                # 中间通配符：/api/*/user
                parts = api.split('*')
                if len(parts) == 2:
                    prefix, suffix = parts
                    if path.startswith(prefix) and path.endswith(suffix):
                        return True
    return False


# def normalize_api_path(path: str) -> str:
#     """
#     标准化 API 路径，将 UUID 替换为 :id
    
#     例如:
#         /api/core/user/123e4567-e89b-12d3-a456-426614174000 -> /api/core/user/:id
#         /api/core/dept/abc123def/users -> /api/core/dept/:id/users
#     """
#     # UUID 正则表达式
#     uuid_pattern = r'[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}'
#     # 替换 UUID 为 :id
#     normalized_path = re.sub(uuid_pattern, ':id', path)
#     return normalized_path

def get_db_style_route(path: str) -> str:
    """
    将请求路径解析为数据库存储的模式
    例如: /api/problem/550e... -> /api/problem/{problem_id}
    """
    try:
        match = resolve(path)
        route = match.route  # 得到 'api/problem/<uuid:problem_id>'
        
        # 使用正则将 <type:name> 或 <name> 转换为 {name}
        # 匹配 <(类型:)?名称>
        db_route = re.sub(r'<(?:[^:>]+:)?([^>]+)>', r'{\1}', route)
        
        # 确保以 / 开头
        if not db_route.startswith('/'):
            db_route = '/' + db_route
        return db_route
    except Resolver404:
        # 如果路径不在 urls.py 中，返回原始路径或进行基础清洗
        return path

class ApiKey(APIKeyQuery):
    """API Key 认证（用于特殊场景，如文件流）"""
    param_name = "token"

    def authenticate(self, request, key):
        """验证 API Key"""
        verify_token(key)
        path = request.path
        # 文件流等特殊接口直接返回
        if path.startswith('/api/core/file_manager/stream/'):
            return key
        return None


class BearerAuth(HttpBearer):
    """
    Bearer Token 认证和权限校验
    基于 Core 模块的权限结构
    """

    def authenticate(self, request, token):
        """
        验证 token 并进行权限校验
        
        :param request: Django request 对象
        :param token: JWT token
        :return: user object or raise HttpError
        """
        try:
            path = request.path
            method = request.method

            # 1. 验证 token
            payload = verify_token(token, token_type="access")
            if not payload:
                raise HttpError(401, "令牌无效或已过期")

            # 2. 获取用户
            user_id = payload.get('id')
            if not user_id:
                raise HttpError(401, "令牌数据无效")

            # 使用 Core 模块的 User 模型
            from core.user.user_model import User
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                raise HttpError(401, "用户不存在")

            # 3. 检查用户状态
            if not user.is_active:
                raise HttpError(403, "用户账户已被禁用")

            # 4. 演示环境保护（全局检查）
            if IS_DEMO and method != 'GET':
                raise HttpError(403, "演示环境不允许修改操作")

            # 5. 超级管理员直接通过
            if user.is_superuser:
                logger.debug(f"超级管理员访问: {path}")
                return user

            # 6. 检查白名单 API
            cached_white_apis = cache.get('white_apis')
            white_apis = API_WHITE_LIST if cached_white_apis is None else [
                *cached_white_apis,
                *API_WHITE_LIST
            ]
            if is_in_white_list(path, white_apis):
                logger.debug(f"白名单 API 访问: {path}")
                return user

            # 7. 权限校验（使用 Core 模块的 Permission）
            has_permission = self._check_permission(user, path, method)
            if has_permission:
                return user
            else:
                logger.warning(f"用户 {user.username} 无权限访问: {method} {path}")
                raise HttpError(403, "无访问权限")

        except HttpError:
            raise
        except Exception as e:
            logger.error(f"认证失败: {str(e)}", exc_info=True)
            raise HttpError(401, "认证失败")

    # def _check_permission(self, user, path: str, method: str) -> bool:
    #     """
    #     检查用户是否有权限访问指定的 API
        
    #     :param user: 用户对象
    #     :param path: API 路径
    #     :param method: HTTP 方法
    #     :return: True 如果有权限，否则 False
    #     """
    #     try:
    #         # 标准化路径（将 UUID 替换为 :id）
    #         normalized_path = normalize_api_path(path)

    #         # 获取 HTTP 方法对应的数字
    #         method_code = HTTP_METHOD_MAP.get(method)
    #         if method_code is None:
    #             logger.warning(f"不支持的 HTTP 方法: {method}")
    #             return False

    #         # 使用缓存提高性能（包含版本号）
    #         from common.fu_cache import PermissionCacheManager
    #         version_key = PermissionCacheManager.get_cache_version_key(user.id)
    #         cache_key = f"user_permission:{user.id}:{version_key}:{normalized_path}:{method}"
    #         cached_result = cache.get(cache_key)
    #         if cached_result is not None:
    #             logger.debug(f"命中权限缓存: {cache_key}")
    #             return cached_result

    #         # 从 Core 模块导入 Permission 模型
    #         from core.permission.permission_model import Permission

    #         # 获取用户所有角色的权限
    #         # user.core_roles 是 ManyToMany 关系
    #         role_ids = list(user.core_roles.filter(status=True).values_list('id', flat=True))

    #         if not role_ids:
    #             logger.debug(f"用户 {user.username} 没有关联任何启用的角色")
    #             cache.set(cache_key, False, 300)  # 缓存5分钟
    #             return False

    #         # 查询权限
    #         # Role.permission 是 ManyToMany 关系，关联到 Permission
    #         # Permission 有 api_path 和 http_method 字段
    #         has_permission = Permission.objects.filter(
    #             roles__id__in=role_ids,  # 通过角色反向查询权限
    #             api_path=normalized_path,
    #             http_method__in=[method_code, 5],  # 5 表示 ALL (所有方法)
    #             is_active=True,
    #         ).exists()

    #         # 缓存结果（5分钟）
    #         cache.set(cache_key, has_permission, 300)

    #         if has_permission:
    #             logger.debug(f"用户 {user.username} 有权限访问: {method} {normalized_path}")

    #         return has_permission

    #     except Exception as e:
    #         logger.error(f"权限检查失败: {str(e)}", exc_info=True)
    #         return False

    def _check_permission(self, user, path: str, method: str) -> bool:
        """
        检查用户是否有权限访问指定的 API
        
        :param user: 用户对象
        :param path: API 路径
        :param method: HTTP 方法
        :return: True 如果有权限，否则 False
        """
        try:
            # 1. 获取数据库风格的路径模式 (例如: /api/problem/{problem_id})
            # 注意：传入的是原始 path，不能是已经替换过 :id 的路径
            db_route_path = get_db_style_route(path)
            
            # 2. 获取 HTTP 方法代码
            method_code = HTTP_METHOD_MAP.get(method)
            if method_code is None:
                return False

            # 3. 缓存逻辑
            from common.fu_cache import PermissionCacheManager
            version_key = PermissionCacheManager.get_cache_version_key(user.id)
            # 注意：缓存 key 建议使用转换后的路径
            cache_key = f"user_perm:{user.id}:{version_key}:{db_route_path}:{method}"
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # 4. 获取角色 IDs
            role_ids = list(user.core_roles.filter(status=True).values_list('id', flat=True))
            if not role_ids:
                return False

            # 5. 从数据库查询
            from core.permission.permission_model import Permission
            
            # 直接匹配转换后的路径
            has_permission = Permission.objects.filter(
                roles__id__in=role_ids,
                api_path=db_route_path,  # 此时匹配的是 /api/problem/{problem_id}
                http_method__in=[method_code, 5],
                is_active=True,
            ).exists()

            # 6. 设置缓存并返回
            cache.set(cache_key, has_permission, 300)
            return has_permission

        except Exception as e:
            logger.error(f"权限检查失败: {str(e)}", exc_info=True)
            return False

def create_token(data: dict):
    """
    创建 access token 和 refresh token
    
    :param data: 加密数据
    :return: (access_token, refresh_token, access_token_exp_timestamp)
    """
    # 获取超时时间
    access_token_timeout = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    refresh_token_timeout = settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES

    # 尝试从数据库获取配置（兼容旧配置）
    if access_token_timeout is None:
        access_token_timeout = 30  # 默认30分钟

    if refresh_token_timeout is None:
        refresh_token_timeout = 7 * 24 * 60  # 默认7天

    # 计算过期时间
    access_token_expire = datetime.utcnow() + timedelta(minutes=access_token_timeout)
    refresh_token_expire = datetime.utcnow() + timedelta(minutes=refresh_token_timeout)

    # 生成 access token 数据
    access_token_data = data.copy()
    access_token_data.update({
        "exp": access_token_expire,
        "iat": datetime.utcnow(),
        "type": "access",
    })

    # 生成 refresh token 数据（包含更少信息）
    refresh_token_data = {
        "id": data.get("id"),
        "username": data.get("username"),
        "exp": refresh_token_expire,
        "iat": datetime.utcnow(),
        "type": "refresh",
    }

    # 编码 token
    access_token = jwt.encode(
        access_token_data,
        settings.JWT_ACCESS_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    refresh_token = jwt.encode(
        refresh_token_data,
        settings.JWT_REFRESH_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return access_token, refresh_token, timegm(access_token_expire.utctimetuple())


def get_user_by_token(request, token_type="access"):
    """
    通过 token 获取用户
    
    :param request: request 对象
    :param token_type: token 类型 (access 或 refresh)
    :return: 用户对象 或 None
    """
    try:
        # 提取 Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header:
            logger.error("未找到授权头")
            return None

        # 确保格式正确
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            logger.error(f"无效的授权头格式: {parts[0] if parts else 'empty'}")
            return None

        token = parts[1]

        # 验证 token
        payload = verify_token(token, token_type)
        if not payload:
            logger.warning("令牌验证失败")
            return None

        # 获取用户
        user_id = payload.get('id')
        if not user_id:
            logger.error("令牌数据中没有用户ID")
            return None

        try:
            from core.user.user_model import User
            user = User.objects.get(id=user_id)

            # 检查用户是否被禁用
            if not user.is_active:
                logger.warning(f"用户 {user_id} 已被禁用")
                return None

            return user
        except Exception as e:
            logger.error(f"根据 ID {user_id} 获取用户失败: {str(e)}")
            return None

    except Exception as e:
        logger.error(f"get_user_by_token 错误: {str(e)}")
        return None


def verify_token(token, token_type="access"):
    """
    验证 token
    
    :param token: token string
    :param token_type: token 类型 (access 或 refresh)
    :return: 解密后的 token 数据 或 None
    """
    try:
        if not token:
            logger.error("令牌为空")
            return None

        # 选择对应的密钥
        if token_type == "refresh":
            secret_key = settings.JWT_REFRESH_SECRET_KEY
        else:
            secret_key = settings.JWT_ACCESS_SECRET_KEY

        # 解码 token
        payload = jwt.decode(token, secret_key, algorithms=[settings.JWT_ALGORITHM])

        # 验证 token 类型
        if payload.get("type") != token_type:
            logger.error(f"令牌类型不匹配: 期望 {token_type}, 实际 {payload.get('type')}")
            return None

        # 检查黑名单（仅对 access token）
        if token_type == "access":
            user_id = payload.get('id')
            if user_id and TokenBlacklist.is_blacklisted(token, user_id):
                logger.warning(f"令牌已被撤销: 用户 {user_id}")
                return None

        return payload
    except jwt.ExpiredSignatureError:
        logger.error("令牌已过期")
        return None
    except jwt.InvalidTokenError as e:
        logger.error(f"无效的令牌: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"验证令牌错误: {str(e)}")
        return None
