# ************** 默认数据库 配置  ************** #
# ================================================= #
# 数据库类型 MYSQL/SQLSERVER/SQLITE3/POSTGRESQL
import os

DATABASE_TYPE = "POSTGRESQL"
# 数据库地址
DATABASE_HOST = ""
# 数据库端口
DATABASE_PORT = 5323
# 数据库用户名
DATABASE_USER = os.environ.get('DEV_DB_USER', "zq-admin")
# 数据库密码
DATABASE_PASSWORD = os.environ.get('DEV_DB_PASSWORD', "")
# 数据库名
DATABASE_NAME = "zq-admin"

# ================================================= #
# ******** redis配置  *********** #
# ================================================= #
REDIS_PASSWORD = ''
REDIS_HOST = '127.0.0.1'
REDIS_DB = '2'
REDIS_URL = f'redis://:{REDIS_PASSWORD or ""}@{REDIS_HOST}:6379'



# # ================================================= #
# # ******************** JWT 配置 ***************** #
# # ================================================= #

# JWT 密钥从环境变量读取
JWT_ACCESS_SECRET_KEY = os.environ.get(
    'JWT_ACCESS_SECRET_KEY',
    'default-access-secret-key-change-in-production'
)
JWT_REFRESH_SECRET_KEY = os.environ.get(
    'JWT_REFRESH_SECRET_KEY',
    'default-refresh-secret-key-change-in-production'
)



# ================================================= #
# ******** 其他配置 *********** #
# ================================================= #
IS_DEMO = False

# ================================================= #
# ******** OAuth 配置 *********** #
# ================================================= #

# 是否给OAuth登陆用户授予管理员权限（生产环境最好不要这样做）
GRANT_ADMIN_TO_OAUTH_USER = True

# Gitee OAuth
GITEE_CLIENT_ID = os.environ.get('GITEE_CLIENT_ID', 'your-gitee-client-id')
GITEE_CLIENT_SECRET = os.environ.get('GITEE_CLIENT_SECRET', 'your-gitee-client-secret')
# 注意：前端端口是 5777，回调路径是 /oauth/gitee/callback
GITEE_REDIRECT_URI = os.environ.get('GITEE_REDIRECT_URI', 'http://localhost:5777/oauth/gitee/callback')

# GitHub OAuth
GITHUB_CLIENT_ID = os.environ.get('GITHUB_CLIENT_ID', 'your-github-client-id')
GITHUB_CLIENT_SECRET = os.environ.get('GITHUB_CLIENT_SECRET', 'your-github-client-secret')
GITHUB_REDIRECT_URI = os.environ.get('GITHUB_REDIRECT_URI', 'http://localhost:5777/oauth/github/callback')

# QQ 互联 OAuth
QQ_APP_ID = os.environ.get('QQ_APP_ID', 'your-qq-app-id')
QQ_APP_KEY = os.environ.get('QQ_APP_KEY', 'your-qq-app-key')
QQ_REDIRECT_URI = os.environ.get('QQ_REDIRECT_URI', 'http://localhost:5777/oauth/qq/callback')

# Google OAuth
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', 'your-google-client-id')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', 'your-google-client-secret')
GOOGLE_REDIRECT_URI = os.environ.get('GOOGLE_REDIRECT_URI', 'http://localhost:5777/oauth/google/callback')

# 微信开放平台 OAuth
WECHAT_APP_ID = os.environ.get('WECHAT_APP_ID', 'your-wechat-app-id')
WECHAT_APP_SECRET = os.environ.get('WECHAT_APP_SECRET', 'your-wechat-app-secret')
WECHAT_REDIRECT_URI = os.environ.get('WECHAT_REDIRECT_URI', 'http://localhost:5777/oauth/wechat/callback')

# Microsoft OAuth
MICROSOFT_CLIENT_ID = os.environ.get('MICROSOFT_CLIENT_ID', 'your-microsoft-client-id')
MICROSOFT_CLIENT_SECRET = os.environ.get('MICROSOFT_CLIENT_SECRET', 'your-microsoft-client-secret')
MICROSOFT_REDIRECT_URI = os.environ.get('MICROSOFT_REDIRECT_URI', 'http://localhost:5777/oauth/microsoft/callback')
