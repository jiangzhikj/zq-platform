# ZQ Platform - FastAPI Backend

基于 FastAPI 的现代化异步后端服务，使用 SQLAlchemy 异步 ORM + Alembic 数据库迁移 + PostgreSQL。

## 技术栈

- **框架**: FastAPI 0.115+
- **数据库**: PostgreSQL 16+
- **ORM**: SQLAlchemy 2.0+ (异步)
- **迁移**: Alembic
- **认证**: JWT
- **缓存**: Redis
- **Python**: 3.12+

## 项目结构

```
backend-fastapi/
├── app/                      # 核心应用模块
│   ├── config.py            # 配置管理
│   ├── database.py          # 数据库连接
│   ├── base_model.py        # BaseModel 基类
│   ├── base_schema.py       # 通用 Schema
│   ├── base_service.py      # BaseService 基类
│   ├── redis.py             # Redis 缓存
│   └── excel.py             # Excel 工具
├── core/                     # 核心业务模块
│   ├── user/                # 用户管理
│   ├── role/                # 角色管理
│   ├── menu/                # 菜单管理
│   ├── dept/                # 部门管理
│   ├── permission/          # 权限管理
│   └── ...
├── scheduler/               # 定时任务模块
│   ├── model.py
│   ├── service.py
│   └── tasks.py
├── zq_demo/                 # 示例模块
│   ├── demo/
│   └── demo_cache/
├── scripts/                 # 工具脚本
│   ├── dumpdata.py         # 数据导出
│   └── loaddata.py         # 数据导入
├── alembic/                 # 数据库迁移
│   ├── versions/
│   └── env.py
├── env/                     # 环境配置
│   ├── dev.env
│   ├── uat.env
│   └── prod.env
├── main.py                  # 应用入口
├── requirements.txt         # 依赖列表
└── README.md
```

## 快速开始

### 1. 环境准备

```bash
# 创建虚拟环境
conda create -n zq-fastapi python=3.12
conda activate zq-fastapi

# 或使用 venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

复制环境配置文件：

```bash
cp env/example.env env/dev.env
```

编辑 `env/dev.env`，配置数据库连接：

```env
# 数据库配置
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname

# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# JWT 配置
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 4. 数据库迁移

```bash
# 首次使用：生成初始迁移
alembic revision --autogenerate -m "init tables"

# 执行迁移
alembic upgrade head

# 导入数据
python scripts/loaddata.py db_init.json
```

### 5. 启动服务

```bash
# 开发模式（自动重载）
python main.py

# 或使用 uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 6. 访问 API 文档

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 数据库操作

### 迁移命令

```bash
# 查看当前版本
alembic current

# 查看迁移历史
alembic history

# 生成新的迁移文件
alembic revision --autogenerate -m "描述信息"

# 升级到最新版本
alembic upgrade head

# 回滚一个版本
alembic downgrade -1

# 回滚到指定版本
alembic downgrade <revision_id>
```

### 数据导入导出

```bash
# 导出所有数据
python scripts/dumpdata.py -o db_init.json -f

# 导出指定模块（如 core）
python scripts/dumpdata.py core -o core_data.json -f

# 导入数据
python scripts/loaddata.py db_init.json
```

## 开发指南

### 新建业务模块

按照以下步骤创建新的业务模块（以 `example` 为例）：

#### 1. 创建模块目录

```bash
mkdir -p core/example
touch core/example/__init__.py
touch core/example/model.py
touch core/example/schema.py
touch core/example/service.py
touch core/example/api.py
```

#### 2. 定义模型 (model.py)

```python
from sqlalchemy import Column, String, Boolean
from app.base_model import BaseModel

class Example(BaseModel):
    __tablename__ = "core_example"
    
    name = Column(String(100), nullable=False, comment="名称")
    description = Column(String(500), comment="描述")
    is_active = Column(Boolean, default=True, comment="是否激活")
```

#### 3. 定义 Schema (schema.py)

```python
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class ExampleBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True

class ExampleCreate(ExampleBase):
    pass

class ExampleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class ExampleResponse(ExampleBase):
    id: str
    sort: int = 0
    is_deleted: bool = False
    sys_create_datetime: Optional[datetime] = None
    sys_update_datetime: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)
```

#### 4. 定义服务 (service.py)

```python
from app.base_service import BaseService
from core.example.model import Example
from core.example.schema import ExampleCreate, ExampleUpdate

class ExampleService(BaseService[Example, ExampleCreate, ExampleUpdate]):
    model = Example
```

#### 5. 定义 API (api.py)

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.base_schema import PaginatedResponse, ResponseModel
from core.example.schema import ExampleCreate, ExampleUpdate, ExampleResponse
from core.example.service import ExampleService

router = APIRouter(prefix="/example", tags=["示例管理"])

@router.post("", response_model=ExampleResponse, summary="创建")
async def create(data: ExampleCreate, db: AsyncSession = Depends(get_db)):
    return await ExampleService.create(db=db, data=data)

@router.get("", response_model=PaginatedResponse[ExampleResponse], summary="获取列表")
async def get_list(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100, alias="pageSize"),
    db: AsyncSession = Depends(get_db)
):
    items, total = await ExampleService.get_list(db, page=page, page_size=page_size)
    return PaginatedResponse(items=items, total=total)

@router.get("/{record_id}", response_model=ExampleResponse, summary="获取详情")
async def get_by_id(record_id: str, db: AsyncSession = Depends(get_db)):
    result = await ExampleService.get_by_id(db, record_id=record_id)
    if not result:
        raise HTTPException(status_code=404, detail="记录不存在")
    return result

@router.put("/{record_id}", response_model=ExampleResponse, summary="更新")
async def update(record_id: str, data: ExampleUpdate, db: AsyncSession = Depends(get_db)):
    result = await ExampleService.update(db, record_id=record_id, data=data)
    if not result:
        raise HTTPException(status_code=404, detail="记录不存在")
    return result

@router.delete("/{record_id}", response_model=ResponseModel, summary="删除")
async def delete(record_id: str, db: AsyncSession = Depends(get_db)):
    success = await ExampleService.delete(db, record_id=record_id)
    if not success:
        raise HTTPException(status_code=404, detail="记录不存在")
    return ResponseModel(message="删除成功")
```

#### 6. 注册路由

在 `core/router.py` 中添加：

```python
from core.example.api import router as example_router

router.include_router(example_router)
```

#### 7. 生成数据库迁移

```bash
alembic revision --autogenerate -m "add example table"
alembic upgrade head
```

## 核心功能

### BaseModel

所有模型继承自 `BaseModel`，自动包含以下字段：

- `id`: UUID 主键
- `sort`: 排序字段
- `is_deleted`: 软删除标记
- `sys_create_datetime`: 创建时间
- `sys_update_datetime`: 更新时间
- `sys_creator_id`: 创建人ID
- `sys_modifier_id`: 修改人ID

### BaseService

提供通用 CRUD 操作：

- `create()`: 创建记录
- `get_by_id()`: 根据ID获取
- `get_list()`: 分页查询
- `update()`: 更新记录
- `delete()`: 删除记录（软删除/硬删除）
- `check_unique()`: 唯一性检查
- `export_to_excel()`: 导出Excel
- `import_from_excel()`: 导入Excel

### 缓存支持

使用 Redis 缓存，继承 `CacheService` 获得缓存功能：

```python
from app.cache_service import CacheService

class ExampleService(CacheService[Example, ExampleCreate, ExampleUpdate]):
    model = Example
    cache_prefix = "example"
    cache_ttl = 3600  # 1小时
```

## 环境配置

项目支持多环境配置：

- `env/dev.env`: 开发环境
- `env/uat.env`: UAT环境
- `env/prod.env`: 生产环境

通过环境变量 `ENV` 切换：

```bash
export ENV=prod  # 使用生产环境配置
python main.py
```

## API 规范

### 响应格式

成功响应：

```json
{
  "code": 200,
  "message": "success",
  "data": {...}
}
```

分页响应：

```json
{
  "items": [...],
  "total": 100
}
```

错误响应：

```json
{
  "detail": "错误信息"
}
```

### 路由命名规范

- 使用小写短横线：`/api/core/user-profile`
- 静态路由在前：`/api/core/menu/check/name`
- 动态路由在后：`/api/core/menu/{menu_id}`

## 常见问题

### 1. 迁移文件为空

确保 `alembic/env.py` 中的 `auto_import_models()` 函数正确扫描了所有模型文件。

### 2. 路由重定向 307

检查路由定义，使用 `@router.post("")` 而不是 `@router.post("/")`。

### 3. 数据库连接失败

检查 `env/dev.env` 中的 `DATABASE_URL` 配置是否正确。

## 许可证

MIT License
