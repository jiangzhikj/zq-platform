#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OAuth Service - OAuth 业务逻辑层
处理第三方 OAuth 登录逻辑
"""
import logging
import requests
from typing import Dict, Optional

from application import settings
from core.oauth.base_oauth_service import BaseOAuthService

logger = logging.getLogger(__name__)


class GiteeOAuthService(BaseOAuthService):
    """Gitee OAuth 服务类"""
    
    PROVIDER_NAME = 'gitee'
    AUTHORIZE_URL = "https://gitee.com/oauth/authorize"
    TOKEN_URL = "https://gitee.com/oauth/token"
    USER_INFO_URL = "https://gitee.com/api/v5/user"
    
    @classmethod
    def get_client_config(cls) -> Dict[str, str]:
        """获取 Gitee 客户端配置"""
        return {
            'client_id': settings.GITEE_CLIENT_ID,
            'client_secret': settings.GITEE_CLIENT_SECRET,
            'redirect_uri': settings.GITEE_REDIRECT_URI,
        }
    
    @classmethod
    def get_user_info(cls, access_token: str) -> Optional[Dict]:
        """
        使用访问令牌获取 Gitee 用户信息
        
        Args:
            access_token: 访问令牌
        
        Returns:
            Optional[Dict]: 用户信息字典，失败返回 None
        """
        try:
            params = {'access_token': access_token}
            response = requests.get(
                cls.USER_INFO_URL,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            user_info = response.json()
            
            if 'id' not in user_info:
                logger.error(f"Gitee 用户信息格式错误: {user_info}")
                return None
            
            return user_info
            
        except requests.RequestException as e:
            logger.error(f"请求 Gitee 用户信息失败: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"获取 Gitee 用户信息异常: {str(e)}")
            return None
    
    @classmethod
    def normalize_user_info(cls, raw_user_info: Dict) -> Dict:
        """
        标准化 Gitee 用户信息
        
        Args:
            raw_user_info: Gitee 原始用户信息
        
        Returns:
            Dict: 标准化后的用户信息
        """
        return {
            'provider_id': str(raw_user_info.get('id')),
            'username': raw_user_info.get('login'),
            'name': raw_user_info.get('name', raw_user_info.get('login')),
            'email': raw_user_info.get('email'),
            'avatar': raw_user_info.get('avatar_url'),
            'bio': raw_user_info.get('bio'),
        }


class GitHubOAuthService(BaseOAuthService):
    """GitHub OAuth 服务类"""
    
    PROVIDER_NAME = 'github'
    AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
    TOKEN_URL = "https://github.com/login/oauth/access_token"
    USER_INFO_URL = "https://api.github.com/user"
    
    @classmethod
    def get_client_config(cls) -> Dict[str, str]:
        """获取 GitHub 客户端配置"""
        return {
            'client_id': settings.GITHUB_CLIENT_ID,
            'client_secret': settings.GITHUB_CLIENT_SECRET,
            'redirect_uri': settings.GITHUB_REDIRECT_URI,
        }
    
    @classmethod
    def get_extra_authorize_params(cls) -> Dict[str, str]:
        """GitHub 需要 scope 参数"""
        return {
            'scope': 'user:email',  # 请求用户邮箱权限
        }
    
    @classmethod
    def get_token_request_headers(cls) -> Dict[str, str]:
        """GitHub 需要 Accept header 来获取 JSON 响应"""
        return {
            'Accept': 'application/json',
        }
    
    @classmethod
    def get_user_info(cls, access_token: str) -> Optional[Dict]:
        """
        使用访问令牌获取 GitHub 用户信息
        
        Args:
            access_token: 访问令牌
        
        Returns:
            Optional[Dict]: 用户信息字典，失败返回 None
        """
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json',
            }
            response = requests.get(
                cls.USER_INFO_URL,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            user_info = response.json()
            
            if 'id' not in user_info:
                logger.error(f"GitHub 用户信息格式错误: {user_info}")
                return None
            
            return user_info
            
        except requests.RequestException as e:
            logger.error(f"请求 GitHub 用户信息失败: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"获取 GitHub 用户信息异常: {str(e)}")
            return None
    
    @classmethod
    def normalize_user_info(cls, raw_user_info: Dict) -> Dict:
        """
        标准化 GitHub 用户信息
        
        Args:
            raw_user_info: GitHub 原始用户信息
        
        Returns:
            Dict: 标准化后的用户信息
        """
        return {
            'provider_id': str(raw_user_info.get('id')),
            'username': raw_user_info.get('login'),
            'name': raw_user_info.get('name') or raw_user_info.get('login'),
            'email': raw_user_info.get('email'),
            'avatar': raw_user_info.get('avatar_url'),
            'bio': raw_user_info.get('bio'),
        }


class QQOAuthService(BaseOAuthService):
    """QQ 互联 OAuth 服务类"""
    
    PROVIDER_NAME = 'qq'
    AUTHORIZE_URL = "https://graph.qq.com/oauth2.0/authorize"
    TOKEN_URL = "https://graph.qq.com/oauth2.0/token"
    USER_INFO_URL = "https://graph.qq.com/user/get_user_info"
    OPENID_URL = "https://graph.qq.com/oauth2.0/me"
    
    @classmethod
    def get_client_config(cls) -> Dict[str, str]:
        """获取 QQ 客户端配置"""
        return {
            'client_id': settings.QQ_APP_ID,
            'client_secret': settings.QQ_APP_KEY,
            'redirect_uri': settings.QQ_REDIRECT_URI,
        }
    
    @classmethod
    def get_extra_authorize_params(cls) -> Dict[str, str]:
        """QQ 需要 response_type 参数"""
        return {
            'response_type': 'code',
        }
    
    @classmethod
    def get_access_token(cls, code: str) -> Optional[str]:
        """
        使用授权码获取访问令牌
        
        QQ 返回的是 URL 参数格式，需要特殊处理
        
        Args:
            code: 授权码
        
        Returns:
            Optional[str]: 访问令牌，失败返回 None
        """
        try:
            config = cls.get_client_config()
            
            params = {
                'grant_type': 'authorization_code',
                'client_id': config['client_id'],
                'client_secret': config['client_secret'],
                'code': code,
                'redirect_uri': config['redirect_uri'],
            }
            
            response = requests.get(
                cls.TOKEN_URL,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            # QQ 返回的是 URL 参数格式: access_token=xxx&expires_in=xxx
            response_text = response.text
            
            # 解析 access_token
            import re
            match = re.search(r'access_token=([^&]+)', response_text)
            if match:
                access_token = match.group(1)
                logger.info(f"QQ access_token 获取成功")
                return access_token
            else:
                logger.error(f"QQ access_token 解析失败: {response_text}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"请求 QQ access_token 失败: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"获取 QQ access_token 异常: {str(e)}")
            return None
    
    @classmethod
    def get_user_info(cls, access_token: str) -> Optional[Dict]:
        """
        使用访问令牌获取 QQ 用户信息
        
        QQ 需要先获取 openid，再获取用户信息
        
        Args:
            access_token: 访问令牌
        
        Returns:
            Optional[Dict]: 用户信息字典，失败返回 None
        """
        try:
            # 1. 获取 openid
            openid_response = requests.get(
                cls.OPENID_URL,
                params={'access_token': access_token},
                timeout=10
            )
            openid_response.raise_for_status()
            
            # QQ 返回的是 JSONP 格式: callback( {"client_id":"xxx","openid":"xxx"} );
            openid_text = openid_response.text
            
            # 解析 openid
            import json
            import re
            match = re.search(r'callback\(\s*(\{.*?\})\s*\)', openid_text)
            if not match:
                logger.error(f"QQ openid 解析失败: {openid_text}")
                return None
            
            openid_data = json.loads(match.group(1))
            openid = openid_data.get('openid')
            
            if not openid:
                logger.error(f"QQ openid 不存在: {openid_data}")
                return None
            
            logger.info(f"QQ openid 获取成功: {openid}")
            
            # 2. 获取用户信息
            config = cls.get_client_config()
            user_response = requests.get(
                cls.USER_INFO_URL,
                params={
                    'access_token': access_token,
                    'oauth_consumer_key': config['client_id'],
                    'openid': openid
                },
                timeout=10
            )
            user_response.raise_for_status()
            
            user_info = user_response.json()
            
            # 检查返回状态
            if user_info.get('ret') != 0:
                logger.error(f"QQ 用户信息获取失败: {user_info.get('msg')}")
                return None
            
            # 将 openid 添加到用户信息中
            user_info['openid'] = openid
            
            return user_info
            
        except requests.RequestException as e:
            logger.error(f"请求 QQ 用户信息失败: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"获取 QQ 用户信息异常: {str(e)}")
            return None
    
    @classmethod
    def normalize_user_info(cls, raw_user_info: Dict) -> Dict:
        """
        标准化 QQ 用户信息
        
        Args:
            raw_user_info: QQ 原始用户信息
        
        Returns:
            Dict: 标准化后的用户信息
        """
        return {
            'provider_id': raw_user_info.get('openid'),
            'username': raw_user_info.get('nickname', '').replace(' ', '_'),  # QQ 昵称可能有空格
            'name': raw_user_info.get('nickname'),
            'email': None,  # QQ 不提供邮箱
            'avatar': raw_user_info.get('figureurl_qq_2') or raw_user_info.get('figureurl_qq_1'),
            'bio': None,
        }


class GoogleOAuthService(BaseOAuthService):
    """Google OAuth 服务类"""
    
    PROVIDER_NAME = 'google'
    AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    USER_INFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
    
    @classmethod
    def get_client_config(cls) -> Dict[str, str]:
        """获取 Google 客户端配置"""
        return {
            'client_id': settings.GOOGLE_CLIENT_ID,
            'client_secret': settings.GOOGLE_CLIENT_SECRET,
            'redirect_uri': settings.GOOGLE_REDIRECT_URI,
        }
    
    @classmethod
    def get_extra_authorize_params(cls) -> Dict[str, str]:
        """Google 需要 scope 和 access_type 参数"""
        return {
            'scope': 'openid email profile',
            'access_type': 'offline',
            'response_type': 'code',
        }
    
    @classmethod
    def get_user_info(cls, access_token: str) -> Optional[Dict]:
        """
        使用访问令牌获取 Google 用户信息
        
        Args:
            access_token: 访问令牌
        
        Returns:
            Optional[Dict]: 用户信息字典，失败返回 None
        """
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
            }
            response = requests.get(
                cls.USER_INFO_URL,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            user_info = response.json()
            
            if 'id' not in user_info:
                logger.error(f"Google 用户信息格式错误: {user_info}")
                return None
            
            return user_info
            
        except requests.RequestException as e:
            logger.error(f"请求 Google 用户信息失败: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"获取 Google 用户信息异常: {str(e)}")
            return None
    
    @classmethod
    def normalize_user_info(cls, raw_user_info: Dict) -> Dict:
        """
        标准化 Google 用户信息
        
        Args:
            raw_user_info: Google 原始用户信息
        
        Returns:
            Dict: 标准化后的用户信息
        """
        return {
            'provider_id': raw_user_info.get('id'),
            'username': raw_user_info.get('email', '').split('@')[0],  # 使用邮箱前缀作为用户名
            'name': raw_user_info.get('name') or raw_user_info.get('email'),
            'email': raw_user_info.get('email'),
            'avatar': raw_user_info.get('picture'),
            'bio': None,
        }


class WeChatOAuthService(BaseOAuthService):
    """微信开放平台 OAuth 服务类"""
    
    PROVIDER_NAME = 'wechat'
    AUTHORIZE_URL = "https://open.weixin.qq.com/connect/qrconnect"
    TOKEN_URL = "https://api.weixin.qq.com/sns/oauth2/access_token"
    USER_INFO_URL = "https://api.weixin.qq.com/sns/userinfo"
    
    @classmethod
    def get_user_id_field(cls) -> str:
        """微信使用 unionid 作为唯一标识"""
        return 'wechat_unionid'
    
    @classmethod
    def get_client_config(cls) -> Dict[str, str]:
        """获取微信客户端配置"""
        return {
            'client_id': settings.WECHAT_APP_ID,
            'client_secret': settings.WECHAT_APP_SECRET,
            'redirect_uri': settings.WECHAT_REDIRECT_URI,
        }
    
    @classmethod
    def get_extra_authorize_params(cls) -> Dict[str, str]:
        """微信需要 appid 和 scope 参数"""
        config = cls.get_client_config()
        return {
            'appid': config['client_id'],  # 微信使用 appid 而不是 client_id
            'scope': 'snsapi_login',  # 网页扫码登录
            'response_type': 'code',
        }
    
    @classmethod
    def get_authorize_url(cls, state: Optional[str] = None) -> str:
        """
        获取微信授权 URL
        微信的参数名称与标准 OAuth 2.0 不同
        """
        config = cls.get_client_config()
        extra_params = cls.get_extra_authorize_params()
        
        params = {
            'appid': config['client_id'],
            'redirect_uri': config['redirect_uri'],
            'response_type': 'code',
            'scope': extra_params['scope'],
        }
        
        if state:
            params['state'] = state
        
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        # 微信需要添加 #wechat_redirect 锚点
        return f"{cls.AUTHORIZE_URL}?{query_string}#wechat_redirect"
    
    @classmethod
    def get_access_token(cls, code: str) -> Optional[Dict]:
        """
        使用授权码获取访问令牌
        微信的参数名称与标准 OAuth 2.0 不同
        
        Returns:
            Dict: 包含 access_token 和 openid
        """
        try:
            config = cls.get_client_config()
            params = {
                'appid': config['client_id'],      # 微信用 appid
                'secret': config['client_secret'],  # 微信用 secret
                'code': code,
                'grant_type': 'authorization_code',
            }
            
            response = requests.get(
                cls.TOKEN_URL,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            token_data = response.json()
            
            # 检查错误
            if 'errcode' in token_data:
                logger.error(f"微信获取 token 失败: {token_data}")
                return None
            
            if 'access_token' not in token_data or 'openid' not in token_data:
                logger.error(f"微信 token 响应格式错误: {token_data}")
                return None
            
            return token_data
            
        except requests.RequestException as e:
            logger.error(f"请求微信 token 失败: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"获取微信 token 异常: {str(e)}")
            return None
    
    @classmethod
    def get_user_info(cls, access_token: str, openid: str = None) -> Optional[Dict]:
        """
        使用访问令牌获取微信用户信息
        微信需要同时传递 access_token 和 openid
        
        Args:
            access_token: 访问令牌
            openid: 用户的 openid
        
        Returns:
            Optional[Dict]: 用户信息字典，失败返回 None
        """
        try:
            params = {
                'access_token': access_token,
                'openid': openid,
                'lang': 'zh_CN',
            }
            
            response = requests.get(
                cls.USER_INFO_URL,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            user_info = response.json()
            
            # 检查错误
            if 'errcode' in user_info:
                logger.error(f"微信获取用户信息失败: {user_info}")
                return None
            
            if 'openid' not in user_info:
                logger.error(f"微信用户信息格式错误: {user_info}")
                return None
            
            return user_info
            
        except requests.RequestException as e:
            logger.error(f"请求微信用户信息失败: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"获取微信用户信息异常: {str(e)}")
            return None
    
    @classmethod
    def normalize_user_info(cls, raw_user_info: Dict) -> Dict:
        """
        标准化微信用户信息
        
        Args:
            raw_user_info: 微信原始用户信息
        
        Returns:
            Dict: 标准化后的用户信息
        """
        # 优先使用 unionid，如果没有则使用 openid
        provider_id = raw_user_info.get('unionid') or raw_user_info.get('openid')
        
        # 微信昵称可能包含 emoji 和特殊字符，需要处理
        nickname = raw_user_info.get('nickname', '')
        username = nickname.replace(' ', '_')[:30] if nickname else f"wechat_{provider_id[:8]}"
        
        return {
            'provider_id': provider_id,
            'username': username,
            'name': nickname or username,
            'email': None,  # 微信不提供邮箱
            'avatar': raw_user_info.get('headimgurl'),
            'bio': None,
        }
    
    @classmethod
    def handle_oauth_login(cls, code: str, state: Optional[str] = None) -> Optional[Dict]:
        """
        处理微信 OAuth 登录流程
        重写此方法以处理微信特殊的 token 响应
        """
        # 1. 获取 access_token 和 openid
        token_data = cls.get_access_token(code)
        if not token_data:
            return None
        
        access_token = token_data.get('access_token')
        openid = token_data.get('openid')
        
        if not access_token or not openid:
            logger.error("微信 token 数据缺少必要字段")
            return None
        
        # 2. 获取用户信息（需要传递 openid）
        raw_user_info = cls.get_user_info(access_token, openid)
        if not raw_user_info:
            return None
        
        # 3. 标准化用户信息
        user_info = cls.normalize_user_info(raw_user_info)
        
        # 4. 创建或更新用户
        user = cls.create_or_update_user(user_info)
        if not user:
            return None
        
        # 5. 生成 JWT token
        return cls.generate_tokens(user)


class MicrosoftOAuthService(BaseOAuthService):
    """微软 OAuth 服务类 (Microsoft Identity Platform)"""
    
    PROVIDER_NAME = 'microsoft'
    AUTHORIZE_URL = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
    TOKEN_URL = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
    USER_INFO_URL = "https://graph.microsoft.com/v1.0/me"
    
    @classmethod
    def get_client_config(cls) -> Dict[str, str]:
        """获取微软客户端配置"""
        return {
            'client_id': settings.MICROSOFT_CLIENT_ID,
            'client_secret': settings.MICROSOFT_CLIENT_SECRET,
            'redirect_uri': settings.MICROSOFT_REDIRECT_URI,
        }
    
    @classmethod
    def get_extra_authorize_params(cls) -> Dict[str, str]:
        """微软需要 scope 和 response_mode 参数"""
        return {
            'scope': 'openid email profile User.Read',
            'response_type': 'code',
            'response_mode': 'query',
        }
    
    @classmethod
    def get_user_info(cls, access_token: str) -> Optional[Dict]:
        """
        使用 Microsoft Graph API 获取用户信息
        
        Args:
            access_token: 访问令牌
        
        Returns:
            Optional[Dict]: 用户信息字典，失败返回 None
        """
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
            }
            response = requests.get(
                cls.USER_INFO_URL,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            user_info = response.json()
            
            if 'id' not in user_info:
                logger.error(f"Microsoft 用户信息格式错误: {user_info}")
                return None
            
            return user_info
            
        except requests.RequestException as e:
            logger.error(f"请求 Microsoft 用户信息失败: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"获取 Microsoft 用户信息异常: {str(e)}")
            return None
    
    @classmethod
    def normalize_user_info(cls, raw_user_info: Dict) -> Dict:
        """
        标准化微软用户信息
        
        Args:
            raw_user_info: Microsoft 原始用户信息
        
        Returns:
            Dict: 标准化后的用户信息
        """
        # 使用 userPrincipalName 的前缀作为用户名
        user_principal_name = raw_user_info.get('userPrincipalName', '')
        username = user_principal_name.split('@')[0] if '@' in user_principal_name else user_principal_name
        
        # 优先使用 mail，如果没有则使用 userPrincipalName
        email = raw_user_info.get('mail') or raw_user_info.get('userPrincipalName')
        
        return {
            'provider_id': raw_user_info.get('id'),
            'username': username or f"ms_{raw_user_info.get('id', '')[:8]}",
            'name': raw_user_info.get('displayName') or username,
            'email': email,
            'avatar': None,  # Microsoft Graph 需要额外 API 调用获取头像
            'bio': raw_user_info.get('jobTitle'),
        }


class DingTalkOAuthService(BaseOAuthService):
    """钉钉 OAuth 服务类
    
    钉钉 OAuth 文档：
    https://open.dingtalk.com/document/orgapp/tutorial-obtaining-user-personal-information
    """
    
    PROVIDER_NAME = 'dingtalk'
    
    # 钉钉扫码登录授权地址
    AUTHORIZE_URL = "https://login.dingtalk.com/oauth2/auth"
    
    # 钉钉获取 access_token 地址
    TOKEN_URL = "https://api.dingtalk.com/v1.0/oauth2/userAccessToken"
    
    # 钉钉获取用户信息地址
    USER_INFO_URL = "https://api.dingtalk.com/v1.0/contact/users/me"
    
    @classmethod
    def get_client_config(cls) -> Dict[str, str]:
        """获取钉钉客户端配置"""
        return {
            'client_id': settings.DINGTALK_APP_ID,
            'client_secret': settings.DINGTALK_APP_SECRET,
            'redirect_uri': settings.DINGTALK_REDIRECT_URI,
        }
    
    @classmethod
    def get_extra_authorize_params(cls) -> Dict[str, str]:
        """钉钉需要的额外授权参数"""
        return {
            'response_type': 'code',
            'scope': 'openid',  # 获取用户基本信息
            'prompt': 'consent',  # 每次都显示授权页面
        }
    
    @classmethod
    def get_access_token(cls, code: str) -> Optional[str]:
        """
        使用授权码获取访问令牌
        
        钉钉的 token 获取方式与标准 OAuth2 不同：
        - 使用 POST 请求
        - 参数在 JSON body 中
        - 返回格式也不同
        
        Args:
            code: 授权码
        
        Returns:
            Optional[str]: 访问令牌，失败返回 None
        """
        try:
            config = cls.get_client_config()
            
            # 钉钉使用 JSON body 传递参数
            data = {
                'clientId': config['client_id'],
                'clientSecret': config['client_secret'],
                'code': code,
                'grantType': 'authorization_code',
            }
            
            headers = {
                'Content-Type': 'application/json',
            }
            
            response = requests.post(
                cls.TOKEN_URL,
                json=data,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            result = response.json()
            
            # 钉钉返回格式: {"accessToken": "xxx", "refreshToken": "xxx", "expireIn": 7200}
            if 'accessToken' in result:
                logger.info(f"钉钉 access_token 获取成功")
                return result['accessToken']
            else:
                logger.error(f"钉钉 token 响应格式错误: {result}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"请求钉钉 access_token 失败: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"获取钉钉 access_token 异常: {str(e)}")
            return None
    
    @classmethod
    def get_user_info(cls, access_token: str) -> Optional[Dict]:
        """
        使用访问令牌获取钉钉用户信息
        
        Args:
            access_token: 访问令牌
        
        Returns:
            Optional[Dict]: 用户信息字典，失败返回 None
        """
        try:
            headers = {
                'x-acs-dingtalk-access-token': access_token,
                'Content-Type': 'application/json',
            }
            
            response = requests.get(
                cls.USER_INFO_URL,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            user_info = response.json()
            
            # 钉钉返回格式检查
            if 'unionId' not in user_info:
                logger.error(f"钉钉用户信息格式错误: {user_info}")
                return None
            
            return user_info
            
        except requests.RequestException as e:
            logger.error(f"请求钉钉用户信息失败: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"获取钉钉用户信息异常: {str(e)}")
            return None
    
    @classmethod
    def normalize_user_info(cls, raw_user_info: Dict) -> Dict:
        """
        标准化钉钉用户信息
        
        钉钉用户信息格式：
        {
            "unionId": "xxx",
            "openId": "xxx",
            "nick": "张三",
            "avatarUrl": "https://...",
            "mobile": "13800138000",
            "email": "xxx@example.com"
        }
        
        Args:
            raw_user_info: 钉钉原始用户信息
        
        Returns:
            Dict: 标准化后的用户信息
        """
        # 使用 unionId 作为唯一标识
        provider_id = raw_user_info.get('unionId', '')
        
        # 钉钉的昵称字段
        nick = raw_user_info.get('nick', '')
        
        # 生成用户名（使用 nick 或 unionId 的一部分）
        username = nick if nick else f"dingtalk_{provider_id[:8]}"
        
        return {
            'provider_id': provider_id,
            'username': username,
            'name': nick or username,
            'email': raw_user_info.get('email'),
            'avatar': raw_user_info.get('avatarUrl'),
            'mobile': raw_user_info.get('mobile'),
            'bio': f"钉钉用户 - {nick}" if nick else "钉钉用户",
        }
    
    @classmethod
    def get_user_id_field(cls) -> str:
        """
        获取用户 ID 字段名
        
        Returns:
            str: 字段名 'dingtalk_unionid'
        """
        return 'dingtalk_unionid'


class FeishuOAuthService(BaseOAuthService):
    """飞书 OAuth 服务类
    
    飞书 OAuth 文档：
    https://open.feishu.cn/document/common-capabilities/sso/api/get-user-info
    """
    
    PROVIDER_NAME = 'feishu'
    
    # 飞书网页应用登录授权地址
    AUTHORIZE_URL = "https://open.feishu.cn/open-apis/authen/v1/authorize"
    
    # 飞书获取 access_token 地址
    TOKEN_URL = "https://open.feishu.cn/open-apis/authen/v1/oidc/access_token"
    
    # 飞书获取用户信息地址
    USER_INFO_URL = "https://open.feishu.cn/open-apis/authen/v1/user_info"
    
    @classmethod
    def get_client_config(cls) -> Dict[str, str]:
        """获取飞书客户端配置"""
        return {
            'client_id': settings.FEISHU_APP_ID,
            'client_secret': settings.FEISHU_APP_SECRET,
            'redirect_uri': settings.FEISHU_REDIRECT_URI,
        }
    
    @classmethod
    def get_extra_authorize_params(cls) -> Dict[str, str]:
        """飞书需要的额外授权参数"""
        return {
            'response_type': 'code',
            'scope': 'contact:user.base:readonly',  # 获取用户基本信息
        }
    
    @classmethod
    def get_access_token(cls, code: str) -> Optional[str]:
        """
        使用授权码获取访问令牌
        
        飞书的 token 获取方式：
        - 使用 POST 请求
        - 参数在 JSON body 中
        - 需要先获取 app_access_token
        
        Args:
            code: 授权码
        
        Returns:
            Optional[str]: 访问令牌，失败返回 None
        """
        try:
            config = cls.get_client_config()
            
            # 飞书使用 JSON body 传递参数
            data = {
                'grant_type': 'authorization_code',
                'code': code,
            }
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {cls._get_app_access_token()}',
            }
            
            response = requests.post(
                cls.TOKEN_URL,
                json=data,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            result = response.json()
            
            # 飞书返回格式: {"code": 0, "msg": "success", "data": {"access_token": "xxx", ...}}
            if result.get('code') == 0 and 'data' in result:
                access_token = result['data'].get('access_token')
                if access_token:
                    logger.info(f"飞书 access_token 获取成功")
                    return access_token
            
            logger.error(f"飞书 token 响应格式错误: {result}")
            return None
                
        except requests.RequestException as e:
            logger.error(f"请求飞书 access_token 失败: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"获取飞书 access_token 异常: {str(e)}")
            return None
    
    @classmethod
    def _get_app_access_token(cls) -> Optional[str]:
        """
        获取应用级别的 access_token（用于调用飞书 API）
        
        Returns:
            Optional[str]: 应用 access_token
        """
        try:
            config = cls.get_client_config()
            
            url = "https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal"
            data = {
                'app_id': config['client_id'],
                'app_secret': config['client_secret'],
            }
            
            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('code') == 0:
                return result.get('app_access_token')
            
            logger.error(f"获取飞书 app_access_token 失败: {result}")
            return None
            
        except Exception as e:
            logger.error(f"获取飞书 app_access_token 异常: {str(e)}")
            return None
    
    @classmethod
    def get_user_info(cls, access_token: str) -> Optional[Dict]:
        """
        使用访问令牌获取飞书用户信息
        
        Args:
            access_token: 访问令牌
        
        Returns:
            Optional[Dict]: 用户信息字典，失败返回 None
        """
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
            }
            
            response = requests.get(
                cls.USER_INFO_URL,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            result = response.json()
            
            # 飞书返回格式检查
            if result.get('code') == 0 and 'data' in result:
                user_info = result['data']
                if 'union_id' not in user_info:
                    logger.error(f"飞书用户信息格式错误: {result}")
                    return None
                return user_info
            
            logger.error(f"飞书用户信息响应错误: {result}")
            return None
            
        except requests.RequestException as e:
            logger.error(f"请求飞书用户信息失败: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"获取飞书用户信息异常: {str(e)}")
            return None
    
    @classmethod
    def normalize_user_info(cls, raw_user_info: Dict) -> Dict:
        """
        标准化飞书用户信息
        
        飞书用户信息格式：
        {
            "union_id": "xxx",
            "user_id": "xxx",
            "open_id": "xxx",
            "name": "张三",
            "en_name": "Zhang San",
            "avatar_url": "https://...",
            "avatar_thumb": "https://...",
            "avatar_middle": "https://...",
            "avatar_big": "https://...",
            "email": "xxx@example.com",
            "mobile": "+86-13800138000"
        }
        
        Args:
            raw_user_info: 飞书原始用户信息
        
        Returns:
            Dict: 标准化后的用户信息
        """
        # 使用 union_id 作为唯一标识
        provider_id = raw_user_info.get('union_id', '')
        
        # 飞书的名称字段
        name = raw_user_info.get('name', '')
        en_name = raw_user_info.get('en_name', '')
        
        # 生成用户名（优先使用英文名，否则使用中文名或 union_id 的一部分）
        username = en_name or name or f"feishu_{provider_id[:8]}"
        # 替换空格为下划线
        username = username.replace(' ', '_')
        
        # 处理手机号（飞书返回格式：+86-13800138000）
        mobile = raw_user_info.get('mobile', '')
        if mobile and mobile.startswith('+86-'):
            mobile = mobile[4:]  # 去掉 +86-
        
        return {
            'provider_id': provider_id,
            'username': username,
            'name': name or username,
            'email': raw_user_info.get('email'),
            'avatar': raw_user_info.get('avatar_url') or raw_user_info.get('avatar_big'),
            'mobile': mobile,
            'bio': f"飞书用户 - {name}" if name else "飞书用户",
        }
    
    @classmethod
    def get_user_id_field(cls) -> str:
        """
        获取用户 ID 字段名
        
        Returns:
            str: 字段名 'feishu_union_id'
        """
        return 'feishu_union_id'
