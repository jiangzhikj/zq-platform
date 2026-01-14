# zq-platform (ZhiQing Development Platform)

English | [简体中文](./README.zh-CN.md)

<div align="center">

A modern enterprise-level admin management system with dual backend options (Django/FastAPI) + Vue3 + Element Plus

[![Django](https://img.shields.io/badge/Django-5.2.7-green.svg)](https://www.djangoproject.com/)
[![Vue](https://img.shields.io/badge/Vue-3.x-brightgreen.svg)](https://vuejs.org/)
[![Element Plus](https://img.shields.io/badge/Element%20Plus-latest-blue.svg)](https://element-plus.org/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

</div>

## Demo Link
### Explorer Version
[https://explorer.zq-platform.cn](https://explorer.zq-platform.cn/)
### Django
[https://django-ninja.zq-platform.cn](https://django-ninja.zq-platform.cn/)
### FastAPI
[https://fastapi.zq-platform.cn](https://fastapi.zq-platform.cn/)

## 📞 Contact & Cooperation

For questions or suggestions, please contact us via:

- Issue: [GitHub Issues](../../issues)
- Email: jiangzhikj@outlook.com
- WeChat: dlpuzcl

## 📖 Introduction

zq-platform is a comprehensive enterprise-level admin management system solution with a separated frontend and backend architecture. It offers two backend options: Django 5.2 + Django Ninja or FastAPI + SQLAlchemy async ORM, while the frontend is based on Vue 3 + Vben Admin + Element Plus to create a modern management interface.

### ✨ Core Features

- 🎯 **Complete RBAC Permission System** - Multi-dimensional permission control for users, roles, permissions, departments, and positions
- 🔐 **JWT Authentication** - Secure token authentication with Access Token and Refresh Token support
- 📊 **System Monitoring** - Server monitoring, Redis monitoring, database monitoring for real-time system status
- 📁 **File Management** - Comprehensive file upload, download, and preview functionality
- 📝 **Operation Logs** - Detailed login logs and operation auditing
- 🗂️ **Data Dictionary** - Flexible dictionary management with multi-level classification support
- ⏰ **Task Scheduling** - APScheduler-based scheduled task management
- 🔌 **WebSocket Support** - Real-time communication capabilities
- 🌐 **Multi-Database Support** - MySQL, PostgreSQL, SQL Server, SQLite
- 🎨 **Modern UI** - Responsive design with dark mode support
- 📦 **Monorepo Architecture** - Frontend engineering solution based on pnpm workspace

## 🏗️ Tech Stack

### Backend Technologies

**Django Backend (backend-django)**
- **Core Framework**: Django 5.2.7
- **API Framework**: Django Ninja 1.4.5 (High-performance API framework)
- **Authentication**: PyJWT 2.8.0
- **Task Scheduling**: APScheduler 3.10.4
- **Caching**: Redis + django-redis
- **WebSocket**: Django Channels 4.2
- **Database Drivers**: psycopg2-binary, pymysql, pyodbc
- **Server**: Uvicorn 0.38.0 / Gunicorn 23.0.0
- **Others**: openpyxl, geoip2, psutil, cryptography

**FastAPI Backend (backend-fastapi)**
- **Core Framework**: FastAPI 0.115+
- **ORM**: SQLAlchemy 2.0+ (Async)
- **Database**: PostgreSQL 16+
- **Migration**: Alembic
- **Authentication**: JWT
- **Caching**: Redis
- **Python**: 3.12+

### Frontend Technologies

- **Core Framework**: Vue 3.x
- **Build Tool**: Vite 5.x
- **UI Component Library**: Element Plus
- **State Management**: Pinia
- **Router**: Vue Router
- **HTTP Client**: Axios
- **Utility Libraries**: VueUse, dayjs, lodash-es
- **Code Standards**: ESLint, Prettier, Stylelint
- **Package Manager**: pnpm 10.14.0
- **Monorepo**: Turbo

## 📁 Project Structure

```
zq-platform/
├── backend-django/          # Django Backend
│   ├── application/         # Project Configuration
│   ├── core/               # Core Business Modules
│   │   ├── auth/           # Authentication & Authorization
│   │   ├── user/           # User Management
│   │   ├── role/           # Role Management
│   │   ├── permission/     # Permission Management
│   │   ├── dept/           # Department Management
│   │   ├── post/           # Position Management
│   │   ├── menu/           # Menu Management
│   │   ├── dict/           # Dictionary Management
│   │   ├── login_log/      # Login Logs
│   │   ├── file_manager/   # File Management
│   │   ├── server_monitor/ # Server Monitoring
│   │   ├── redis_monitor/  # Redis Monitoring
│   │   ├── redis_manager/  # Redis Management
│   │   ├── database_monitor/ # Database Monitoring
│   │   └── database_manager/ # Database Management
│   ├── scheduler/          # Task Scheduling Module
│   ├── common/             # Common Modules
│   ├── env/                # Environment Configuration
│   ├── requirements.txt    # Python Dependencies
│   └── manage.py          # Django Management Script
│
├── backend-fastapi/         # FastAPI Backend (Optional)
│   ├── app/                # Core Application Module
│   ├── core/               # Core Business Modules
│   ├── scheduler/          # Task Scheduling Module
│   ├── scripts/            # Utility Scripts
│   ├── alembic/            # Database Migration
│   ├── env/                # Environment Configuration
│   ├── requirements.txt    # Python Dependencies
│   └── main.py            # Application Entry
│
└── web/                    # Vue Frontend (Monorepo)
    ├── apps/
    │   └── web-ele/        # Element Plus Main Application
    │       ├── src/
    │       │   ├── api/    # API Interfaces
    │       │   ├── views/  # Page Components
    │       │   ├── router/ # Router Configuration
    │       │   └── store/  # State Management
    │       └── package.json
    ├── packages/           # Shared Packages
    │   ├── @core/          # Core Packages
    │   ├── effects/        # Effects Packages
    │   ├── hooks/          # Hooks
    │   ├── icons/          # Icons
    │   ├── locales/        # Internationalization
    │   ├── stores/         # State Management
    │   └── utils/          # Utility Functions
    ├── internal/           # Internal Tools
    └── package.json        # Root Configuration
```

## 🚀 Quick Start

### Requirements

- **Backend**
  - Python >= 3.10
  - MySQL >= 5.7 / PostgreSQL >= 12 / SQL Server
  - Redis >= 5.0

- **Frontend**
  - Node.js >= 20.10.0
  - pnpm >= 9.12.0

### Backend Installation

#### Option 1: Django Backend (Recommended for Production)

1. **Clone the Project**
```bash
git clone https://github.com/jiangzhikj/zq-platform.git
cd zq-platform/backend-django
```

2. **Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure Environment Variables**
```bash
cp env
# Edit the .env file to configure database, Redis, JWT keys, etc.
```

Main configuration items:
```env

# JWT Keys
JWT_ACCESS_SECRET_KEY=your-jwt-access-secret
JWT_REFRESH_SECRET_KEY=your-jwt-refresh-secret

# Database Configuration
DATABASE_TYPE=MYSQL  # MYSQL/POSTGRESQL/SQLSERVER/SQLITE3
DATABASE_HOST=127.0.0.1
DATABASE_PORT=3306
DATABASE_USER=root
DATABASE_PASSWORD=password
DATABASE_NAME=zq_admin

# Redis Configuration
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=2
```

5. **Database Migration**
```bash
python manage.py makemigrations core scheduler
python manage.py migrate
```

6. **Initialize Data**
```bash
python manage.py loaddata db_init.json
```

7. **Start Service**
```bash
# Development Environment
python manage.py runserver 0.0.0.0:8000

```

8. **Start Task Scheduler (Optional)**
```bash
# Production Environment
python start_scheduler.py
```

#### Option 2: FastAPI Backend (Recommended for High Performance)

1. **Navigate to FastAPI Directory**
```bash
cd zq-platform/backend-fastapi
```

2. **Create Virtual Environment**
```bash
conda create -n zq-fastapi python=3.12
conda activate zq-fastapi
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure Environment Variables**
```bash
cp env/example.env env/dev.env
# Edit env/dev.env to configure database connection
```

5. **Database Migration**
```bash
alembic revision --autogenerate -m "init tables"
alembic upgrade head

# Import initial data (optional)
python scripts/loaddata.py db_init.json
```

6. **Start Service**
```bash
python main.py
# or
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

7. **Access API Documentation**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Frontend Installation

1. **Navigate to Frontend Directory**
```bash
cd zq-platform/web
```

2. **Install Dependencies**
```bash
pnpm install
```

3. **Configure Environment Variables**
```bash
cd apps/web-ele
cp .env.development .env
# Edit the .env file to configure backend API address
```

4. **Start Development Server**
```bash
# In web root directory
pnpm dev
```

5. **Build for Production**
```bash
pnpm build:ele
```

## 📝 Default Account

After initializing data, you can login with the following account:

- Username: `superadmin`
- Password: `123456` or contact administrator

## 🔧 Main Functional Modules

### System Management
- **User Management**: CRUD operations for users, password reset, status management
- **Role Management**: Role permission assignment, data permission control
- **Permission Management**: Fine-grained API and button permission control
- **Department Management**: Tree-structured department management
- **Position Management**: Position information maintenance
- **Menu Management**: Dynamic menu configuration, route management
- **Dictionary Management**: System dictionary maintenance

### System Monitoring
- **Server Monitoring**: Real-time monitoring of CPU, memory, disk, network
- **Redis Monitoring**: Redis performance metrics, key-value management
- **Database Monitoring**: Database connection, performance monitoring
- **Login Logs**: User login records, IP geolocation

### Task Scheduling
- **Scheduled Tasks**: Cron expression configuration
- **Task Logs**: Execution history, result viewing
- **Task Management**: Start, stop, execute immediately

### File Management
- **File Upload**: Multi-file upload support
- **File Preview**: Online preview for images and documents
- **File Download**: Batch download functionality

## 🔐 API Documentation

**Django Backend**
- Swagger UI: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`

**FastAPI Backend**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🛠️ Development Guide

### Backend Development

1. **Adding New Modules**
   - Create in `core/` or create a new app
   - Define models, schemas, services, api
   - Register routes in router

2. **API Development Standards**
   - Use Django Ninja decorators
   - Unified return format
   - Exception handling
   - Permission verification

### Frontend Development

1. **Adding New Pages**
   - Create page components in `src/views/`
   - Add routes in `src/router/routes/modules/`
   - Add API definitions in `src/api/`

2. **Component Development Standards**
   - Use Element Plus components
   - Prefer Tailwind CSS
   - Support dark mode
   - Import icons from `@vben/icons`

## 📦 Deployment
1. **Backend Deployment**
   - Use Gunicorn + Nginx
   - Configure Supervisor process daemon
   - Configure SSL certificates

2. **Frontend Deployment**
   - Execute `pnpm build` to build
   - Deploy `dist` directory to Nginx
   - Configure reverse proxy

## 🤝 Contributing

Issues and Pull Requests are welcome!

1. Fork this project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


## 🙏 Acknowledgments

- [Django](https://www.djangoproject.com/) - Powerful Python web framework
- [Django Ninja](https://django-ninja.rest-framework.com/) - Fast Django REST framework
- [Vue Vben Admin](https://github.com/vbenjs/vue-vben-admin) - Excellent Vue3 admin template
- [Element Plus](https://element-plus.org/) - Vue 3 component library

---

<div align="center">
  Made with ❤️ by ZQ Team
</div>
