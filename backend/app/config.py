import os
from typing import Any, Literal, Optional
from urllib.parse import quote_plus

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置"""
    # 环境标识
    ENV: Literal["dev", "uat", "prod"] = "dev"
    DEBUG: bool = False
    
    # 应用配置
    APP_NAME: str = "FastAPI Demo"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    
    # 数据库配置
    DB_TYPE: Literal["postgresql", "mysql", "sqlserver"] = "postgresql"  # 数据库类型
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = ""
    DB_NAME: str = "fastapi_db"
    
    # 数据库连接URL（可手动配置，否则根据 DB_TYPE 自动拼接）
    DATABASE_URL: Optional[str] = None
    
    # 分页配置
    PAGE_SIZE: int = 20
    PAGE_MAX_SIZE: int = 100
    
    # 时区配置（IANA时区名称，如 Asia/Shanghai, America/New_York, UTC 等）
    TIMEZONE: str = "Asia/Shanghai"
    
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
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # Access Token过期时间（分钟）
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # Refresh Token过期时间（天）
    ALLOW_MULTI_DEVICE_LOGIN: bool = True  # 是否允许多设备同时登录（False=单设备登录，新登录会踢掉旧设备）

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
    GRANT_ADMIN_TO_OAUTH_USER: bool = True  # 是否给OAuth用户授予管理员权限
    OAUTH_DEFAULT_DEPT_ID: Optional[str] = 'fbsamU5f2VNtjAJhpGJdy'  # OAuth用户默认部门ID
    # Gitee OAuth
    GITEE_CLIENT_ID: Optional[str] = None
    GITEE_CLIENT_SECRET: Optional[str] = None
    GITEE_REDIRECT_URI: Optional[str] = 'https://explorer.zq-platform.cn/oauth/gitee/callback'
    # GitHub OAuth
    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None
    GITHUB_REDIRECT_URI: Optional[str] = 'https://explorer.zq-platform.cn/oauth/github/callback'
    # QQ OAuth
    QQ_APP_ID: Optional[str] = None
    QQ_APP_KEY: Optional[str] = None
    QQ_REDIRECT_URI: Optional[str] = 'https://explorer.zq-platform.cn/oauth/qq/callback'
    # Google OAuth
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: Optional[str] = 'https://explorer.zq-platform.cn/oauth/google/callback'
    # 微信 OAuth
    WECHAT_APP_ID: Optional[str] = None
    WECHAT_APP_SECRET: Optional[str] = None
    WECHAT_REDIRECT_URI: Optional[str] = 'https://explorer.zq-platform.cn/oauth/wechat/callback'
    # Microsoft OAuth
    MICROSOFT_CLIENT_ID: Optional[str] = None
    MICROSOFT_CLIENT_SECRET: Optional[str] = None
    MICROSOFT_REDIRECT_URI: Optional[str] = 'https://explorer.zq-platform.cn/oauth/microsoft/callback'
    # 钉钉 OAuth
    DINGTALK_APP_ID: Optional[str] = None
    DINGTALK_APP_SECRET: Optional[str] = None
    DINGTALK_REDIRECT_URI: Optional[str] = 'https://localhost:5777/oauth/dingtalk/callback'
    # 飞书 OAuth
    FEISHU_APP_ID: Optional[str] = None
    FEISHU_APP_SECRET: Optional[str] = None
    FEISHU_REDIRECT_URI: Optional[str] = 'https://localhost:5777/oauth/feishu/callback'
    # 企业微信 OAuth
    WECOM_CORP_ID: Optional[str] = None
    WECOM_AGENT_ID: Optional[str] = None
    WECOM_APP_SECRET: Optional[str] = None
    WECOM_REDIRECT_URI: Optional[str] = 'https://localhost:5777/oauth/wecom/callback'

    # SMTP 邮件配置
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 465
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_USE_TLS: bool = True
    SMTP_FROM_NAME: Optional[str] = None  # 发件人显示名称，默认使用 APP_NAME
    SMTP_FROM_EMAIL: Optional[str] = None  # 发件人邮箱，默认使用 SMTP_USER

    # 钉钉通知配置
    DINGTALK_WEBHOOK_URL: Optional[str] = None  # 群机器人 Webhook 地址
    DINGTALK_WEBHOOK_SECRET: Optional[str] = None  # 群机器人签名密钥
    DINGTALK_AGENT_ID: Optional[str] = None  # 企业内部应用 AgentId（工作通知需要）
    DINGTALK_CORP_ID: Optional[str] = None  # 企业 CorpId（工作通知需要）

    # 飞书通知配置
    FEISHU_WEBHOOK_URL: Optional[str] = None  # 群机器人 Webhook 地址
    FEISHU_WEBHOOK_SECRET: Optional[str] = None  # 群机器人签名密钥

    # 企业微信通知配置
    WECOM_WEBHOOK_URL: Optional[str] = None  # 群机器人 Webhook 地址

    # 微信公众号模板消息配置（复用 WECHAT_APP_ID / WECHAT_APP_SECRET）
    WECHAT_MP_TEMPLATE_ID: Optional[str] = None  # 模板消息 ID
    WECHAT_MP_URL: Optional[str] = None  # 模板消息点击跳转链接
    WECHAT_MP_MINI_APPID: Optional[str] = None  # 跳转小程序 appid（可选）
    WECHAT_MP_MINI_PAGE: Optional[str] = None  # 跳转小程序页面路径（可选）

    # 短信通知配置
    SMS_PROVIDER: Optional[str] = None  # 短信服务商: aliyun / tencent
    # 阿里云短信
    ALIYUN_SMS_ACCESS_KEY_ID: Optional[str] = None
    ALIYUN_SMS_ACCESS_KEY_SECRET: Optional[str] = None
    ALIYUN_SMS_SIGN_NAME: Optional[str] = None  # 短信签名
    ALIYUN_SMS_TEMPLATE_CODE: Optional[str] = None  # 短信模板编号
    # 腾讯云短信
    TENCENT_SMS_SECRET_ID: Optional[str] = None
    TENCENT_SMS_SECRET_KEY: Optional[str] = None
    TENCENT_SMS_SDK_APP_ID: Optional[str] = None  # 短信应用 SDKAppID
    TENCENT_SMS_SIGN_NAME: Optional[str] = None  # 短信签名
    TENCENT_SMS_TEMPLATE_ID: Optional[str] = None  # 短信模板 ID

    # 系统通知用户（用于聊天通知渠道的发送者）
    SYSTEM_NOTIFY_USER_ID: Optional[str] = None

    # 向量数据库配置（Qdrant）
    VECTOR_STORE_TYPE: str = "qdrant"  # 向量存储类型
    QDRANT_HOST: str = "pro.fuadmin.cn"
    QDRANT_PORT: int = 6333
    QDRANT_GRPC_PORT: int = 6334
    QDRANT_API_KEY: Optional[str] = "9s7k8d2p9x8m7n6b5v4c3x2z1"
    QDRANT_PREFER_GRPC: bool = False

    # 语音，ocr模型key（优先从数据库 LLMProvider qwen 提供商获取，此处作为兜底）
    DASHSCOPE_API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=f"env/{os.getenv('ENV', 'dev')}.env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @field_validator(
        "APP_PORT",
        "DB_PORT",
        "REDIS_PORT",
        "SMTP_PORT",
        "QDRANT_PORT",
        "QDRANT_GRPC_PORT",
        mode="before",
    )
    @classmethod
    def empty_int_uses_default(cls, value: Any, info) -> Any:
        """env 文件中留空时回退到字段默认值，避免 '' 触发 int 校验失败"""
        if value == "" or value is None:
            field = cls.model_fields[info.field_name]
            return field.default
        return value

    @staticmethod
    def _build_db_auth(user: str, password: str) -> str:
        """拼接数据库认证信息，支持空密码（本地 trust 认证常见场景）"""
        user = quote_plus(user)
        if password:
            return f"{user}:{quote_plus(password)}"
        return user

    @model_validator(mode="after")
    def build_urls(self) -> "Settings":
        """自动拼接DATABASE_URL和REDIS_URL"""
        if not self.DATABASE_URL:
            auth = self._build_db_auth(self.DB_USER, self.DB_PASSWORD)
            if self.DB_TYPE == "mysql":
                self.DATABASE_URL = (
                    f"mysql+aiomysql://{auth}"
                    f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
                )
            elif self.DB_TYPE == "sqlserver":
                self.DATABASE_URL = (
                    f"mssql+aioodbc://{auth}"
                    f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
                    f"?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"
                )
            else:
                self.DATABASE_URL = (
                    f"postgresql+asyncpg://{auth}"
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
