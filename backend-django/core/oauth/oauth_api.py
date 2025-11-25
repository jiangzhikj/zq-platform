#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OAuth API - OAuth 接口层
提供第三方 OAuth 登录的 API 接口
"""
import logging
from ninja import Router, Schema
from ninja.errors import HttpError
from django.http import HttpRequest

from .oauth_schema import OAuthCallbackSchema, OAuthLoginResponseSchema
from .oauth_service import (
    GiteeOAuthService, GitHubOAuthService, QQOAuthService, GoogleOAuthService,
    WeChatOAuthService, MicrosoftOAuthService, DingTalkOAuthService, FeishuOAuthService
)

logger = logging.getLogger(__name__)

router = Router()

# OAuth 提供商映射
OAUTH_PROVIDERS = {
    'gitee': GiteeOAuthService,
    'github': GitHubOAuthService,
    'qq': QQOAuthService,
    'google': GoogleOAuthService,
    'wechat': WeChatOAuthService,
    'microsoft': MicrosoftOAuthService,
    'dingtalk': DingTalkOAuthService,
    'feishu': FeishuOAuthService,
}


class AuthorizeUrlOut(Schema):
    """授权 URL 响应"""
    authorize_url: str


@router.get("/{provider}/authorize", response=AuthorizeUrlOut, auth=None, summary="获取 OAuth 授权 URL")
def get_oauth_authorize_url(request: HttpRequest, provider: str):
    """
    获取 OAuth 授权 URL (通用接口)
    
    Args:
        provider: OAuth 提供商 (gitee/github)
    
    前端应该将用户重定向到此 URL
    """
    # 验证 provider
    if provider not in OAUTH_PROVIDERS:
        raise HttpError(status_code=400, message=f"不支持的 OAuth 提供商: {provider}")
    
    try:
        service_class = OAUTH_PROVIDERS[provider]
        # 可以传递 state 参数用于防止 CSRF 攻击
        state = request.GET.get('state', '')
        authorize_url = service_class.get_authorize_url(state)
        
        return AuthorizeUrlOut(authorize_url=authorize_url)
    except Exception as e:
        logger.error(f"获取 {provider} 授权 URL 失败: {str(e)}")
        raise HttpError(status_code=500, message=f"获取授权 URL 失败: {str(e)}")


@router.post("/{provider}/callback", auth=None, response=OAuthLoginResponseSchema, summary="OAuth 回调处理")
def oauth_callback(request: HttpRequest, provider: str, data: OAuthCallbackSchema):
    """
    处理 OAuth 回调 (通用接口)
    
    Args:
        provider: OAuth 提供商 (gitee/github)
        data: 回调数据（包含 code 和 state）
    
    前端在授权后会获得 code，将 code 发送到此接口完成登录
    """
    # 验证 provider
    if provider not in OAUTH_PROVIDERS:
        raise HttpError(status_code=400, message=f"不支持的 OAuth 提供商: {provider}")
    
    try:
        service_class = OAUTH_PROVIDERS[provider]
        
        # 获取客户端 IP 和 User-Agent
        ip_address = request.META.get('REMOTE_ADDR', '')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # 处理 OAuth 登录（传递 provider 作为登录方式）
        user, access_token, refresh_token, expire_time = service_class.handle_oauth_login(
            code=data.code,
            ip_address=ip_address,
            user_agent=user_agent,
            login_type=provider  # 传递登录方式
        )
        
        # 构造返回数据
        user_info = {
            'id': str(user.id),
            'username': user.username,
            'name': user.name,
            'email': user.email,
            'avatar': user.avatar,
            'user_type': user.user_type,
            'is_superuser': user.is_superuser,
        }
        
        logger.info(f"{provider.capitalize()} OAuth 登录成功: {user.username}")
        
        return OAuthLoginResponseSchema(
            access_token=access_token,
            refresh_token=refresh_token,
            expire=expire_time,
            user_info=user_info,
        )
        
    except ValueError as e:
        logger.warning(f"{provider.capitalize()} OAuth 登录失败: {str(e)}")
        raise HttpError(status_code=401, message=str(e))
    except Exception as e:
        logger.error(f"{provider.capitalize()} OAuth 登录异常: {str(e)}", exc_info=True)
        raise HttpError(status_code=500, message="登录失败，请稍后重试")
