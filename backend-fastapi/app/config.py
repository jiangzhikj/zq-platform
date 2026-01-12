#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author: 臧成龙
@Contact: 939589097@qq.com
@Time: 2025-12-31
@File: config.py
@Desc: 应用配置 - # 环境标识
"""
import os
from typing import Literal, Optional

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置"""
    # 环境标识
    ENV: Literal["dev", "uat", "prod"] = "dev"
    DEBUG: bool = True
    
    # 应用配置
    APP_NAME: str = "FastAPI Demo"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    
    # 数据库配置
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = ""
    DB_NAME: str = ""
    
    # 数据库连接URL（可手动配置，否则自动拼接）
    DATABASE_URL: Optional[str] = None
    
    # 分页配置
    PAGE_SIZE: int = 20
    PAGE_MAX_SIZE: int = 100
    
    # Redis配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0
    REDIS_URL: Optional[str] = None
    
    # 缓存配置
    CACHE_DEFAULT_EXPIRE: int = 300  # 默认缓存过期时间（秒）
    CACHE_PREFIX: str = "fastapi:"  # 缓存key前缀
    
    # JWT配置
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"  # JWT密钥，生产环境必须修改
    JWT_ALGORITHM: str = "HS256"  # JWT算法
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # Access Token过期时间（分钟）
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # Refresh Token过期时间（天）

    # 文件存储配置
    FILE_STORAGE_TYPE: str = "minio"  # local/oss/minio/azure
    FILE_STORAGE_LOCAL_PATH: Optional[str] = None  # 本地存储路径
    # OSS配置
    OSS_ENDPOINT: Optional[str] = None
    OSS_ACCESS_KEY_ID: Optional[str] = None
    OSS_ACCESS_KEY_SECRET: Optional[str] = None
    OSS_BUCKET_NAME: Optional[str] = None
    # Minio配置
    MINIO_ENDPOINT: Optional[str] = None
    MINIO_ACCESS_KEY: Optional[str] = None
    MINIO_SECRET_KEY: Optional[str] = None
    MINIO_BUCKET_NAME: Optional[str] = None
    MINIO_SECURE: bool = False
    # Azure配置
    AZURE_ACCOUNT_NAME: Optional[str] = None
    AZURE_ACCOUNT_KEY: Optional[str] = None
    AZURE_CONTAINER_NAME: Optional[str] = None

    # OAuth配置
    GRANT_ADMIN_TO_OAUTH_USER: bool = False  # 是否给OAuth用户授予管理员权限
    # Gitee OAuth
    GITEE_CLIENT_ID: Optional[str] = None
    GITEE_CLIENT_SECRET: Optional[str] = None
    GITEE_REDIRECT_URI: Optional[str] = 'https://fastapi.zq-platform.cn/oauth/gitee/callback'
    # GitHub OAuth
    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None
    GITHUB_REDIRECT_URI: Optional[str] = 'https://fastapi.zq-platform.cn/oauth/github/callback'
    # QQ OAuth
    QQ_APP_ID: Optional[str] = None
    QQ_APP_KEY: Optional[str] = None
    QQ_REDIRECT_URI: Optional[str] = 'https://fastapi.zq-platform.cn/oauth/qq/callback'
    # Google OAuth
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: Optional[str] = 'https://fastapi.zq-platform.cn/oauth/google/callback'
    # 微信 OAuth
    WECHAT_APP_ID: Optional[str] = None
    WECHAT_APP_SECRET: Optional[str] = None
    WECHAT_REDIRECT_URI: Optional[str] = 'https://fastapi.zq-platform.cn/oauth/wechat/callback'
    # Microsoft OAuth
    MICROSOFT_CLIENT_ID: Optional[str] = None
    MICROSOFT_CLIENT_SECRET: Optional[str] = None
    MICROSOFT_REDIRECT_URI: Optional[str] = 'https://fastapi.zq-platform.cn/oauth/microsoft/callback'
    # 钉钉 OAuth
    DINGTALK_APP_ID: Optional[str] = None
    DINGTALK_APP_SECRET: Optional[str] = None
    DINGTALK_REDIRECT_URI: Optional[str] = 'https://localhost:5777/oauth/dingtalk/callback'
    # 飞书 OAuth
    FEISHU_APP_ID: Optional[str] = None
    FEISHU_APP_SECRET: Optional[str] = None
    FEISHU_REDIRECT_URI: Optional[str] = 'https://localhost:5777/oauth/feishu/callback'
    
    model_config = SettingsConfigDict(
        env_file=f"env/{os.getenv('ENV', 'dev')}.env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )
    
    @model_validator(mode="after")
    def build_urls(self) -> "Settings":
        """自动拼接DATABASE_URL和REDIS_URL"""
        if not self.DATABASE_URL:
            self.DATABASE_URL = (
                f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"
                f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            )
        if not self.REDIS_URL:
            if self.REDIS_PASSWORD:
                self.REDIS_URL = (
                    f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
                )
            else:
                self.REDIS_URL = f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return self


def get_settings() -> Settings:
    """根据环境变量加载对应的配置文件"""
    env = os.getenv("ENV", "dev")
    return Settings(_env_file=f"env/{env}.env")


settings = get_settings()
