# zq-platform(芷青开发平台)

[English](./README.md) | 简体中文

<div align="center">

一个现代化的企业级后台管理系统，提供 Django 和 FastAPI 双后端选择 + Vue3 + Element Plus 构建

[![Django](https://img.shields.io/badge/Django-5.2.7-green.svg)](https://www.djangoproject.com/)
[![Vue](https://img.shields.io/badge/Vue-3.x-brightgreen.svg)](https://vuejs.org/)
[![Element Plus](https://img.shields.io/badge/Element%20Plus-latest-blue.svg)](https://element-plus.org/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

</div>

## 演示链接
### 探索无敌版本
[https://explorer.zq-platform.cn](https://explorer.zq-platform.cn/)
### Django
[https://django-ninja.zq-platform.cn](https://django-ninja.zq-platform.cn/)
### FastAPI
[https://fastapi.zq-platform.cn](https://fastapi.zq-platform.cn/)

## 📞 联系合作方式

如有问题或建议，请通过以下方式联系：

- Issue: [GitHub Issues](../../issues)
- Email: jiangzhikj@outlook.com
- 微信: dlpuzcl

## 📖 项目简介

zq-platform 是一个功能完善的企业级后台管理系统解决方案，采用前后端分离架构。提供两种后端选择：Django 5.2 + Django Ninja 或 FastAPI + SQLAlchemy 异步 ORM，前端基于 Vue 3 + Vben Admin + Element Plus 打造现代化的管理界面。

### ✨ 核心特性

- 🎯 **完整的 RBAC 权限系统** - 用户、角色、权限、部门、岗位多维度权限控制
- 🔐 **JWT 认证机制** - 安全的 Token 认证，支持 Access Token 和 Refresh Token
- 📊 **系统监控** - 服务器监控、Redis 监控、数据库监控，实时掌握系统状态
- 📁 **文件管理** - 完善的文件上传、下载、预览功能
- 📝 **操作日志** - 详细的登录日志和操作审计
- 🗂️ **数据字典** - 灵活的字典管理，支持多级分类
- ⏰ **任务调度** - 基于 APScheduler 的定时任务管理
- 🔌 **WebSocket 支持** - 实时通信能力
- 🌐 **多数据库支持** - MySQL、PostgreSQL、SQL Server、SQLite
- 🎨 **现代化 UI** - 响应式设计，支持暗黑模式
- 📦 **Monorepo 架构** - 基于 pnpm workspace 的前端工程化方案

## 🏗️ 技术栈

### 后端技术

**Django 后端 (backend-django)**
- **核心框架**: Django 5.2.7
- **API 框架**: Django Ninja 1.4.5 (高性能 API 框架)
- **认证**: PyJWT 2.8.0
- **任务调度**: APScheduler 3.10.4
- **缓存**: Redis + django-redis
- **WebSocket**: Django Channels 4.2
- **数据库驱动**: psycopg2-binary, pymysql, pyodbc
- **服务器**: Uvicorn 0.38.0 / Gunicorn 23.0.0
- **其他**: openpyxl, geoip2, psutil, cryptography

**FastAPI 后端 (backend-fastapi)**
- **核心框架**: FastAPI 0.115+
- **ORM**: SQLAlchemy 2.0+ (异步)
- **数据库**: PostgreSQL 16+
- **迁移**: Alembic
- **认证**: JWT
- **缓存**: Redis
- **Python**: 3.12+

### 前端技术

- **核心框架**: Vue 3.x
- **构建工具**: Vite 5.x
- **UI 组件库**: Element Plus
- **状态管理**: Pinia
- **路由**: Vue Router
- **HTTP 客户端**: Axios
- **工具库**: VueUse, dayjs, lodash-es
- **代码规范**: ESLint, Prettier, Stylelint
- **包管理**: pnpm 10.14.0
- **Monorepo**: Turbo

## 📁 项目结构

```
zq-platform/
├── backend-django/          # Django 后端
│   ├── application/         # 项目配置
│   ├── core/               # 核心业务模块
│   │   ├── auth/           # 认证授权
│   │   ├── user/           # 用户管理
│   │   ├── role/           # 角色管理
│   │   ├── permission/     # 权限管理
│   │   ├── dept/           # 部门管理
│   │   ├── post/           # 岗位管理
│   │   ├── menu/           # 菜单管理
│   │   ├── dict/           # 字典管理
│   │   ├── login_log/      # 登录日志
│   │   ├── file_manager/   # 文件管理
│   │   ├── server_monitor/ # 服务器监控
│   │   ├── redis_monitor/  # Redis 监控
│   │   ├── redis_manager/  # Redis 管理
│   │   ├── database_monitor/ # 数据库监控
│   │   └── database_manager/ # 数据库管理
│   ├── scheduler/          # 任务调度模块
│   ├── common/             # 公共模块
│   ├── env/                # 环境配置
│   ├── requirements.txt    # Python 依赖
│   └── manage.py          # Django 管理脚本
│
├── backend-fastapi/         # FastAPI 后端（可选）
│   ├── app/                # 核心应用模块
│   ├── core/               # 核心业务模块
│   ├── scheduler/          # 定时任务模块
│   ├── scripts/            # 工具脚本
│   ├── alembic/            # 数据库迁移
│   ├── env/                # 环境配置
│   ├── requirements.txt    # Python 依赖
│   └── main.py            # 应用入口
│
└── web/                    # Vue 前端 (Monorepo)
    ├── apps/
    │   └── web-ele/        # Element Plus 版本主应用
    │       ├── src/
    │       │   ├── api/    # API 接口
    │       │   ├── views/  # 页面组件
    │       │   ├── router/ # 路由配置
    │       │   └── store/  # 状态管理
    │       └── package.json
    ├── packages/           # 共享包
    │   ├── @core/          # 核心包
    │   ├── effects/        # 副作用包
    │   ├── hooks/          # Hooks
    │   ├── icons/          # 图标
    │   ├── locales/        # 国际化
    │   ├── stores/         # 状态管理
    │   └── utils/          # 工具函数
    ├── internal/           # 内部工具
    └── package.json        # 根配置
```

## 🚀 快速开始

### 环境要求

- **后端**
  - Python >= 3.10
  - MySQL >= 5.7 / PostgreSQL >= 12 / SQL Server
  - Redis >= 5.0

- **前端**
  - Node.js >= 20.10.0
  - pnpm >= 9.12.0

### 后端安装

#### 选项 1: Django 后端（推荐用于生产环境）

1. **克隆项目**
```bash
git clone https://github.com/jiangzhikj/zq-platform.git
cd zq-platform/backend-django
```

2. **创建虚拟环境**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **配置环境变量**
```bash
cp env
# 编辑 .env 文件，配置数据库、Redis、JWT 密钥等
```

主要配置项：
```env

# JWT 密钥
JWT_ACCESS_SECRET_KEY=your-jwt-access-secret
JWT_REFRESH_SECRET_KEY=your-jwt-refresh-secret

# 数据库配置
DATABASE_TYPE=MYSQL  # MYSQL/POSTGRESQL/SQLSERVER/SQLITE3
DATABASE_HOST=127.0.0.1
DATABASE_PORT=3306
DATABASE_USER=root
DATABASE_PASSWORD=password
DATABASE_NAME=zq_admin

# Redis 配置
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=2
```

5. **数据库迁移**
```bash
python manage.py makemigrations core scheduler
python manage.py migrate
```

6. **初始化数据**
```bash
python manage.py loaddata db_init.json
```

7. **启动服务**
```bash
# 开发环境
python manage.py runserver 0.0.0.0:8000

```

8. **启动任务调度器（可选）**
```bash
# 生产环境
python start_scheduler.py
```

#### 选项 2: FastAPI 后端（推荐用于高性能场景）

1. **进入 FastAPI 目录**
```bash
cd zq-platform/backend-fastapi
```

2. **创建虚拟环境**
```bash
conda create -n zq-fastapi python=3.12
conda activate zq-fastapi
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **配置环境变量**
```bash
cp env/example.env env/dev.env
# 编辑 env/dev.env 配置数据库连接
```

5. **数据库迁移**
```bash
alembic revision --autogenerate -m "init tables"
alembic upgrade head

# 导入初始数据（可选）
python scripts/loaddata.py db_init.json
```

6. **启动服务**
```bash
python main.py
# 或
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

7. **访问 API 文档**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 前端安装

1. **进入前端目录**
```bash
cd zq-platform/web
```

2. **安装依赖**
```bash
pnpm install
```

3. **配置环境变量**
```bash
cd apps/web-ele
cp .env.development .env
# 编辑 .env 文件，配置后端 API 地址
```

4. **启动开发服务器**
```bash
# 在 web 根目录下
pnpm dev
```

5. **构建生产版本**
```bash
pnpm build:ele
```

## 📝 默认账号

初始化数据后，可使用以下账号登录：

- 账号: `superadmin`
- 密码: 请查看 `123456` 或联系管理员

## 🔧 主要功能模块

### 系统管理
- **用户管理**: 用户的增删改查、密码重置、状态管理
- **角色管理**: 角色权限分配、数据权限控制
- **权限管理**: 接口权限、按钮权限细粒度控制
- **部门管理**: 树形部门结构管理
- **岗位管理**: 岗位信息维护
- **菜单管理**: 动态菜单配置、路由管理
- **字典管理**: 系统字典维护

### 系统监控
- **服务器监控**: CPU、内存、磁盘、网络实时监控
- **Redis 监控**: Redis 性能指标、键值管理
- **数据库监控**: 数据库连接、性能监控
- **登录日志**: 用户登录记录、IP 地理位置

### 任务调度
- **定时任务**: Cron 表达式配置
- **任务日志**: 执行历史、结果查看
- **任务管理**: 启动、停止、立即执行

### 文件管理
- **文件上传**: 支持多文件上传
- **文件预览**: 图片、文档在线预览
- **文件下载**: 批量下载功能

## 🔐 API 文档

**Django 后端**
- Swagger UI: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`

**FastAPI 后端**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🛠️ 开发指南

### 后端开发

1. **添加新模块**
   - 在 `core/` 或创建新 app
   - 定义 models、schemas、services、api
   - 在 router 中注册路由

2. **API 开发规范**
   - 使用 Django Ninja 装饰器
   - 统一返回格式
   - 异常处理
   - 权限验证

### 前端开发

1. **添加新页面**
   - 在 `src/views/` 创建页面组件
   - 在 `src/router/routes/modules/` 添加路由
   - 在 `src/api/` 添加接口定义

2. **组件开发规范**
   - 使用 Element Plus 组件
   - 优先使用 Tailwind CSS
   - 支持暗黑模式
   - 图标从 `@vben/icons` 导入

## 📦 部署
1. **后端部署**
   - 使用 Gunicorn + Nginx
   - 配置 Supervisor 进程守护
   - 配置 SSL 证书

2. **前端部署**
   - 执行 `pnpm build` 构建
   - 将 `dist` 目录部署到 Nginx
   - 配置反向代理

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request


## 🙏 致谢

- [Django](https://www.djangoproject.com/) - 强大的 Python Web 框架
- [Django Ninja](https://django-ninja.rest-framework.com/) - 快速的 Django REST 框架
- [Vue Vben Admin](https://github.com/vbenjs/vue-vben-admin) - 优秀的 Vue3 后台管理模板
- [Element Plus](https://element-plus.org/) - 基于 Vue 3 的组件库
---

<div align="center">
  Made with ❤️ by ZQ Team
</div>
