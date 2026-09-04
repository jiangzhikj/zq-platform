# ZQ Platform

<div align="center">

[![许可证](https://img.shields.io/badge/许可证-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](backend/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.121+-green.svg)](backend/)
[![Vue](https://img.shields.io/badge/Vue-3.5+-brightgreen.svg)](web/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue.svg)](web/)

**一个基于 FastAPI + Vue 3 的全栈企业级低代码/零代码开发平台**

[English](README.en.md) | 简体中文

</div>

## 🌐 相关链接

- **官方网站**：<https://zq-platform.com/>
- **社区版演示**：<https://opensource.zq-platform.com/>
- **演示账号**：zhangwei
- **演示密码**：123456

***

## 📖 项目简介

ZQ Platform 是一个功能完善的全栈企业级开发平台，采用前后端分离架构。后端基于 **FastAPI** 异步框架，前端基于 **Vue 3** + **Element Plus** + **Vben Admin 5.x** 构建。

平台集成了 RBAC 权限管理、组织架构管理、**在线表单/页面设计（零代码）**、即时通讯、AI 对话、第三方登录与组织同步、系统监控、定时任务、数据源管理、代码生成等丰富的企业级功能模块，可大幅加速企业级应用开发。

## 🎯 零代码能力 — 完全开源、免费、无限制

ZQ Platform 的零代码（在线开发）模块是其核心亮点之一，与市面上主流的零代码/低代码平台相比，拥有 **完全开源、完全免费、完全无限制** 的显著优势。

### 与同类平台对比

| 对比维度      | ZQ Platform                  | 钉钉宜搭              | 百度爱速搭             | NocoBase                |
| --------- | ---------------------------- | ----------------- | ----------------- | ----------------------- |
| **开源协议**  | 完全开源                         | ❌ 闭源商业软件          | ❌ 闭源商业软件          | ⚠️ AGPL 3.0（传染性协议，商用受限） |
| **是否免费**  | ✅ 完全免费，无任何隐藏费用               | ❌ 按用户/表单/流程数收费    | ❌ 按版本收费，有功能限制     | ⚠️ 社区版功能受限，企业版收费        |
| **用户数限制** | ✅ 无限制                        | ❌ 按套餐限制用户数        | ❌ 按版本限制用户数        | ⚠️ 社区版有用户限制             |
| **部署方式**  | ✅ 私有化部署，数据完全自主可控             | ⚠️ SaaS为主，私有化成本极高 | ⚠️ SaaS为主，私有化需企业版 | ✅ 支持私有化部署               |
| **二次开发**  | ✅ 无限制，可任意修改源码                | ❌ 不支持             | ❌ 有限支持            | ⚠️ AGPL协议限制商业二次开发       |
| **商用授权**  | ✅ Apache 2.0 协议 + 附加条款，可自由商用 | ❌ 需购买商业许可         | ❌ 需购买商业许可         | ⚠️ AGPL商用需购买授权          |
| **数据库支持** | PostgreSQL / MySQL           | 仅支持云数据库           | 仅支持云数据库           | PostgreSQL              |
| **前端技术**  | Vue 3 + Element Plus（主流技术栈）  | 封闭技术栈，无法自定义       | 封闭技术栈             | React + Ant Design      |
| **后端技术**  | Python FastAPI（异步高性能）        | 封闭                | 封闭                | Node.js + Koa           |

### 零代码核心功能

#### 📝 在线表单设计器

- **拖拽式设计**：直观的拖拽操作，无需编写任何代码即可构建复杂表单
- **丰富组件库**：文本输入、数字、日期、下拉选择、级联选择、文件上传、富文本、子表单等 30+ 组件
- **复杂布局**：支持分栏、分组、表格布局、标签页等复杂页面布局
- **条件逻辑**：支持字段显隐条件、校验规则、联动逻辑配置
- **移动端适配**：自动适配 PC 端与移动端展示

#### 📄 在线页面设计器

- **可视化页面编排**：将表单、图表、数据表格等组件自由组合成完整的业务页面
- **数据绑定**：支持数据源绑定、API 对接，实现页面与后端数据的实时交互
- **权限集成**：页面级别的访问权限控制，与 RBAC 权限体系无缝集成

#### 📊 仪表盘设计器

- **丰富图表组件**：支持折线图、柱状图、饼图、雷达图、漏斗图、热力图、桑基图、K 线图等 20+ 图表类型
- **业务组件**：公告列表、待办事项、快捷入口、排行列表、服务器监控、天气组件等业务组件
- **数据过滤**：支持日期筛选、输入筛选等交互式数据过滤
- **自由布局**：拖拽式自由布局，支持自定义尺寸和位置

#### 🔗 数据管理

- **数据源管理**：支持接入外部数据库（PostgreSQL / MySQL / SQL Server）作为数据源
- **表单数据管理**：自动生成表单数据的列表、详情、编辑和删除功能
- **数据导入导出**：支持 Excel 格式的数据导入与导出

### 适用场景

- **企业内部管理系统**：OA、CRM、ERP、进销存、项目管理等
- **业务流程数字化**：审批流程、工单系统、报表系统等
- **快速原型开发**：业务需求快速验证与迭代
- **SaaS 平台构建**：多租户应用开发
- **数据收集与分析**：调查问卷、数据采集、统计分析

***

## 🏗 技术栈

### 后端 (Backend)

| 技术                                                     | 说明              |
| ------------------------------------------------------ | --------------- |
| [FastAPI](https://fastapi.tiangolo.com/)               | Web 框架 (0.121+) |
| [SQLAlchemy 2.0](https://www.sqlalchemy.org/)          | 异步 ORM          |
| [Alembic](https://alembic.sqlalchemy.org/)             | 数据库迁移           |
| [PostgreSQL 16+](https://www.postgresql.org/) / MySQL  | 数据库             |
| [Redis](https://redis.io/)                             | 缓存与消息           |
| [APScheduler 4.x](https://apscheduler.readthedocs.io/) | 定时任务调度          |
| [MinIO](https://min.io/) / OSS / Azure Blob            | 文件存储            |
| [Qdrant](https://qdrant.tech/)                         | 向量数据库 (RAG)     |
| [OpenAI](https://openai.com/) / Anthropic / DashScope  | AI 大模型集成        |
| [WebSocket](https://websockets.readthedocs.io/)        | 实时通信            |

### 前端 (Frontend)

| 技术                                                         | 说明                      |
| ---------------------------------------------------------- | ----------------------- |
| [Vue 3](https://vuejs.org/)                                | 前端框架                    |
| [TypeScript](https://www.typescriptlang.org/)              | 类型安全                    |
| [Element Plus](https://element-plus.org/)                  | UI 组件库                  |
| [Vben Admin 5.x](https://github.com/vbenjs/vue-vben-admin) | 后台管理框架                  |
| [Vite](https://vitejs.dev/)                                | 构建工具                    |
| [Pinia](https://pinia.vuejs.org/)                          | 状态管理                    |
| [Vue Router](https://router.vuejs.org/)                    | 路由管理                    |
| [i18n](https://vue-i18n.intlify.nuxt.dev/)                 | 国际化 (zh-CN/en-US/zh-TW) |
| [ECharts](https://echarts.apache.org/)                     | 图表可视化                   |
| [Tiptap](https://tiptap.dev/)                              | 富文本编辑器                  |
| [CodeMirror](https://codemirror.net/)                      | 代码编辑器                   |

## ✨ 核心特性

### 🔐 用户与权限

- **用户管理**：完整的用户 CRUD、头像上传、密码策略
- **角色管理**：基于 RBAC 的角色权限分配
- **菜单管理**：动态菜单配置与权限控制
- **部门管理**：树形组织架构管理
- **岗位管理**：岗位关联与人员管理
- **资源权限**：资源级别的细粒度字段权限控制
- **数据权限**：基于部门/用户的数据范围隔离

### 🏢 组织管理

- **组织架构**：可视化组织架构图
- **部门树**：无限级部门层级管理
- **企业同步**：支持钉钉、飞书、企业微信组织架构与用户同步

### 🔗 第三方集成

- **OAuth 登录**：支持 Gitee、GitHub、QQ、Google、微信、Microsoft、钉钉、飞书、企业微信
- **消息通知**：邮件 (SMTP)、短信 (阿里云/腾讯云)、钉钉机器人、飞书机器人、企业微信机器人、微信公众号
- **文件存储**：支持本地存储、MinIO、阿里云 OSS、Azure Blob Storage

### 📱 零代码能力

- **在线表单设计**：拖拽式表单构建器，支持复杂表单设计
- **表单数据管理**：表单数据的 CRUD 与动态查询
- **在线页面设计**：可视化页面编辑器
- **仪表盘设计**：仪表盘设计器，支持丰富图表组件
- **代码生成器**：支持多种编码模式 (日期序列、流水号等)

### 💬 即时通讯

- **实时聊天**：基于 WebSocket 的单聊与群聊
- **消息管理**：未读计数、消息免打扰、置顶会话
- **消息通知**：系统通知与公告管理

### 🤖 AI 能力

- **AI 对话**：集成 OpenAI、Anthropic (Claude)、DashScope (通义千问) 等多种大模型
- **知识库**：基于 Qdrant 向量数据库的 RAG 检索增强生成

### ⚙️ 系统工具

- **数据字典**：业务字典管理 (支持树形/列表)
- **系统配置**：动态系统参数配置
- **UI 配置**：前端界面偏好设置 (可从后端动态加载)
- **定时任务**：基于 APScheduler 的任务调度管理
- **文件管理**：文件上传、预览、分片上传
- **数据源管理**：外部数据库连接管理
- **API 令牌**：API 访问令牌管理
- **区域管理**：省市区地理数据管理

### 🌐 国际化

- 支持中文简体、中文繁体、英文
- 前端 UI 界面完全国际化
- 后端错误消息国际化支持

## 🚀 快速开始

### 前置条件

- Python 3.12+
- Node.js 20.10+
- pnpm 9.12+
- PostgreSQL 16+
- Redis

### 后端启动

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp env/example.env env/dev.env
# 编辑 env/dev.env 配置数据库连接等信息

# 运行数据库迁移
alembic upgrade head

# 初始化数据
python scripts/loaddata.py db_init.json


# 启动开发服务器
uvicorn main:app --reload --port 8000
```

### 前端启动

```bash
cd web

# 安装依赖
pnpm install

# 启动开发服务器（默认使用 Element Plus 版本）
pnpm dev
```

访问 <http://localhost:5777> 即可进入系统。

### 🐳 Docker Compose 一键部署

项目提供了完整的 Docker Compose 部署方案，位于 `docker/` 目录下，可一键启动 PostgreSQL、Redis、后端和前端服务。

#### 前置条件

- [Docker](https://www.docker.com/) >= 24.0
- [Docker Compose](https://docs.docker.com/compose/) >= 2.20

#### 部署步骤

```bash
# 1. 进入项目根目录
cd zq-platform

# 2. （可选）修改环境变量配置
# 编辑 .env 文件，生产环境请务必修改 JWT_SECRET_KEY、DB_PASSWORD、REDIS_PASSWORD
vim .env

# 3. 构建并启动所有服务
docker compose up -d

# 4. 查看启动日志
docker compose logs -f

# 5. 访问系统
# 浏览器打开 http://localhost
```

#### 服务架构

```text
┌─────────────┐      ┌──────────────────────────────────┐
│   Browser   │ ───▶ │     Nginx (Port 80)               │
└─────────────┘      │  ├─ 静态文件 → Vue SPA            │
                     │  ├─ /basic-api/* → backend:8000   │
                     │  └─ /ws/*        → backend:8000   │
                     └──────────┬───────────────────────┘
                                │
         ┌──────────────────────┼──────────────────────┐
         ▼                      ▼                       ▼
  ┌─────────────┐       ┌──────────────┐       ┌──────────────┐
  │ PostgreSQL  │       │    Redis     │       │   Backend    │
  │   :5432     │       │   :6379      │       │   :8000      │
  └─────────────┘       └──────────────┘       └──────────────┘
```

#### 服务说明

| 服务名 | 镜像 | 端口 | 说明 |
|--------|------|------|------|
| **postgres** | postgres:16-alpine | 5432 | 数据库 |
| **redis** | redis:7-alpine | 6379 | 缓存（AOF 持久化） |
| **backend** | 自建 | 8000 | FastAPI（Uvicorn 4 workers） |
| **web** | 自建 | **80** | Nginx 服务前端 + 代理 API/WebSocket |

#### 常用命令

```bash
# 构建并启动
docker compose up -d

# 查看日志
docker compose logs -f

# 停止服务
docker compose down

# 完全清理（会删除数据卷，首次部署时使用）
docker compose down -v

# 仅重建某个服务（修改代码后）
docker compose build backend
docker compose up -d backend

# 查看服务状态
docker compose ps
```

#### 安全注意事项

1. **生产部署前务必修改 `.env` 中的密钥**：
   - `JWT_SECRET_KEY` — JWT 签名密钥
   - `DB_PASSWORD` — 数据库密码
   - `REDIS_PASSWORD` — Redis 密码
2. 默认使用 PostgreSQL，如需切换 MySQL 请修改 `docker-compose.yml` 中的服务配置
3. 文件存储默认使用 `local` 模式，如需 MinIO/OSS 可在 `.env` 中配置


## 🏛 项目结构

```
zq-platform/
├── backend/                          # 后端 Python 服务
│   ├── app/                          # 核心应用模块
│   │   ├── base_model.py            # 基础模型
│   │   ├── base_schema.py           # 通用 Schema
│   │   ├── base_service.py          # 基础服务
│   │   ├── config.py                # 系统配置
│   │   ├── database.py              # 数据库连接
│   │   └── ...
│   ├── core/                         # 核心业务模块
│   │   ├── auth/                    # 认证模块
│   │   ├── user/                    # 用户管理
│   │   ├── role/                    # 角色管理
│   │   ├── menu/                    # 菜单管理
│   │   ├── dept/                    # 部门管理
│   │   ├── permission/              # 权限管理
│   │   ├── chat/                    # 即时通讯
│   │   ├── file_manager/            # 文件管理
│   │   ├── message/                 # 消息通知
│   │   ├── oauth/                   # 第三方登录
│   │   ├── code_generator/          # 代码生成器
│   │   ├── data_source/             # 数据源管理
│   │   ├── system_config/           # 系统配置
│   │   ├── ui_config/               # UI 配置
│   │   ├── server_monitor/          # 服务监控
│   │   ├── redis_monitor/           # Redis 监控
│   │   ├── database_monitor/        # 数据库监控
│   │   ├── redis_manager/           # Redis 管理
│   │   ├── database_manager/        # 数据库管理
│   │   ├── dingtalk_sync/           # 钉钉同步
│   │   ├── feishu_sync/             # 飞书同步
│   │   ├── wecom_sync/              # 企业微信同步
│   │   ├── application/             # 应用管理
│   │   ├── device/                  # 设备管理
│   │   ├── region/                  # 区域管理
│   │   ├── login_log/               # 登录日志
│   │   ├── api_token/               # API 令牌
│   │   ├── link_preview/            # 链接预览
│   │   ├── dict/                    # 数据字典
│   │   ├── post/                    # 岗位管理
│   │   └── resource_scope/          # 资源权限
│   ├── online_dev/                   # 在线开发模块
│   │   ├── form_manager/            # 表单管理
│   │   ├── form_data_manager/       # 表单数据管理
│   │   └── page_manager/            # 页面管理
│   ├── scheduler/                    # 定时任务
│   ├── zq_demo/                      # 示例模块
│   ├── alembic/                      # 数据库迁移
│   ├── main.py                       # 应用入口
│   └── requirements.txt              # Python 依赖
│
├── web/                              # 前端工程
│   ├── apps/
│   │   └── web-ele/                 # Element Plus 版本应用
│   │       └── src/
│   │           ├── api/             # API 接口
│   │           ├── components/      # 业务组件
│   │           ├── views/           # 页面视图
│   │           ├── router/          # 路由配置
│   │           ├── store/           # 状态管理
│   │           ├── locales/         # 国际化
│   │           └── layouts/         # 布局组件
│   ├── packages/                     # 共享包
│   │   ├── @core/                   # 核心包 (UI 组件、工具库等)
│   │   ├── effects/                 # 业务逻辑
│   │   ├── constants/               # 常量定义
│   │   ├── hooks/                   # 组合式函数
│   │   ├── icons/                   # 图标库
│   │   ├── locales/                 # 国际化
│   │   ├── preferences/             # 偏好设置
│   │   ├── request/                 # HTTP 请求
│   │   ├── stores/                  # 状态管理
│   │   ├── styles/                  # 样式
│   │   ├── types/                   # TypeScript 类型
│   │   └── utils/                   # 工具函数
│   └── package.json                  # 前端依赖
│
└── README.md                         # 项目文档
```

## ✅ 环境要求

| 依赖         | 版本要求     |
| ---------- | -------- |
| Python     | >= 3.12  |
| Node.js    | >= 20.10 |
| pnpm       | >= 9.12  |
| PostgreSQL | >= 16    |
| Redis      | >= 6.0   |

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request 来帮助改进项目。

1. Fork 本仓库
2. 创建您的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'feat: 添加某个功能'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 提交 Pull Request

## 📄 许可证

本项目采用双重许可证结构：

- **核心许可**：[Apache License 2.0](LICENSE) — 标准 Apache 2.0 开源协议，允许自由使用、修改和再发布
- **附加条款**：[ZQ-Platform Public License Supplemental Terms](LICENSE_SUPPLEMENTAL) — 包含署名（"powered by ZQ-Platform"）与商标使用的补充约定

使用本代码即表示您同意遵守以上两份文件中的所有条款。

## 📞 联系我们

- **官方网站**：<https://zq-platform.com/>
- **开源仓库**：<https://github.com/jiangzhikj/zq-platform>
- **完整版演示**：<https://demo.zq-platform.com/>
- **开源版演示**：<https://opensource.zq-platform.com/>
- **作者邮箱**：<jiangzhikj@outlook.com>
- **问题反馈**：[GitHub Issues](https://github.com/jiangzhikj/zq-platform/issues)

