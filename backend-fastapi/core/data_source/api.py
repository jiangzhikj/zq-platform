#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Data Source API - 数据源接口
提供数据源的增删改查、执行、测试等功能
"""
import logging
from typing import List, Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.config import settings
from app.base_schema import PaginatedResponse, ResponseModel
from core.data_source.model import DataSource
from core.data_source.schema import (
    DataSourceCreate,
    DataSourceUpdate,
    DataSourceResponse,
    DataSourceSimpleOut,
    DataSourcePreviewRequest,
    DataSourceExecuteRequest,
    DataSourceTestRequest,
    DataSourceCopyRequest,
)
from core.data_source.service import DataSourceService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/data-source", tags=["数据源管理"])


# ============ 静态路径接口（必须放在动态路径之前） ============

@router.get("", response_model=PaginatedResponse[DataSourceResponse], summary="获取数据源列表")
async def list_data_source(
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=settings.PAGE_SIZE, ge=1, le=settings.PAGE_MAX_SIZE, alias="pageSize", description="每页数量"),
    name: str = Query(default=None, description="名称（模糊查询）"),
    code: str = Query(default=None, description="编码（模糊查询）"),
    source_type: str = Query(default=None, alias="sourceType", description="类型"),
    status: bool = Query(default=None, description="状态"),
    db: AsyncSession = Depends(get_db),
):
    """获取数据源列表（分页）"""
    items, total = await DataSourceService.get_list(
        db, page=page, page_size=page_size,
        name=name, code=code, source_type=source_type, status=status,
    )
    return PaginatedResponse(items=items, total=total)


@router.post("", response_model=DataSourceResponse, summary="创建数据源")
async def create_data_source(
    data: DataSourceCreate,
    db: AsyncSession = Depends(get_db),
):
    """创建数据源"""
    # 检查编码是否已存在
    if await DataSourceService.check_code_exists(db, data.code):
        raise HTTPException(status_code=400, detail=f"编码已存在: {data.code}")

    source = await DataSourceService.create(db, data.model_dump())
    await db.commit()
    logger.info(f"数据源已创建: {source.code}")
    return source


@router.get("/get/all", response_model=List[DataSourceSimpleOut], summary="获取所有数据源")
async def list_all_data_source(db: AsyncSession = Depends(get_db)):
    """获取所有数据源（不分页，用于下拉选择）"""
    items = await DataSourceService.get_all(db)
    return items


@router.post("/test", summary="测试数据源配置")
async def test_data_source(
    body: DataSourceTestRequest,
    db: AsyncSession = Depends(get_db),
):
    """测试数据源配置（不保存，直接执行）"""
    try:
        config = {
            'source_type': body.source_type,
            'api_url': body.api_url,
            'api_method': body.api_method,
            'api_headers': body.api_headers,
            'api_body': body.api_body,
            'api_timeout': body.api_timeout,
            'api_data_path': body.api_data_path,
            'sql_content': body.sql_content,
            'db_connection': body.db_connection,
            'static_data': body.static_data,
            'params_def': body.params_def,
            'result_type': body.result_type,
            'tree_config': body.tree_config,
            'field_mapping': body.field_mapping,
            'chart_config': body.chart_config,
        }

        data = await DataSourceService.execute_temp(db, config, body.params)

        total = len(data) if isinstance(data, list) else 1

        return {
            'data': data,
            'total': total,
            'limited': DataSourceService.MAX_ROWS_TEST,
            'success': True
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"数据源测试失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"测试失败: {str(e)}")


@router.get("/check-code/{code}", summary="检查编码是否可用")
async def check_code_available(
    code: str,
    db: AsyncSession = Depends(get_db),
):
    """检查数据源编码是否可用"""
    exists = await DataSourceService.check_code_exists(db, code)
    return {'available': not exists}


# ============ 执行接口 ============

@router.get("/execute/{code}", summary="执行数据源（GET）")
async def execute_data_source_get(
    request: Request,
    code: str,
    db: AsyncSession = Depends(get_db),
):
    """根据编码执行数据源获取数据（GET 方式）"""
    # 获取所有查询参数
    params = dict(request.query_params)

    try:
        data = await DataSourceService.execute(db, code, params)
        return {'data': data}
    except ValueError as e:
        if "不存在" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"数据源执行失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"执行失败: {str(e)}")


@router.post("/execute/{code}", summary="执行数据源（POST）")
async def execute_data_source_post(
    code: str,
    body: DataSourceExecuteRequest,
    db: AsyncSession = Depends(get_db),
):
    """根据编码执行数据源获取数据（POST 方式）"""
    try:
        data = await DataSourceService.execute(db, code, body.params)
        return {'data': data}
    except ValueError as e:
        if "不存在" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"数据源执行失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"执行失败: {str(e)}")


# ============ 动态路径接口（必须放在静态路径之后） ============

@router.get("/{source_id}", response_model=DataSourceResponse, summary="获取数据源详情")
async def get_data_source(
    source_id: str,
    db: AsyncSession = Depends(get_db),
):
    """获取数据源详情"""
    source = await DataSourceService.get_by_id(db, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="数据源不存在")
    return source


@router.put("/{source_id}", response_model=DataSourceResponse, summary="更新数据源")
async def update_data_source(
    source_id: str,
    data: DataSourceUpdate,
    db: AsyncSession = Depends(get_db),
):
    """更新数据源"""
    # 如果更新了编码，检查新编码是否已存在
    if data.code:
        if await DataSourceService.check_code_exists(db, data.code, exclude_id=source_id):
            raise HTTPException(status_code=400, detail=f"编码已存在: {data.code}")

    source = await DataSourceService.update(db, source_id, data.model_dump(exclude_unset=True))
    if not source:
        raise HTTPException(status_code=404, detail="数据源不存在")
    await db.commit()
    logger.info(f"数据源已更新: {source.code}")
    return source


@router.delete("/{source_id}", response_model=ResponseModel, summary="删除数据源")
async def delete_data_source(
    source_id: str,
    db: AsyncSession = Depends(get_db),
):
    """删除数据源"""
    success = await DataSourceService.delete(db, source_id)
    if not success:
        raise HTTPException(status_code=404, detail="数据源不存在")
    await db.commit()
    return ResponseModel(message="删除成功")


# ============ 预览和其他接口 ============

@router.post("/{source_id}/preview", summary="预览数据源数据")
async def preview_data_source(
    source_id: str,
    body: DataSourcePreviewRequest,
    db: AsyncSession = Depends(get_db),
):
    """预览数据源数据（用于调试）"""
    try:
        data = await DataSourceService.execute_by_id(db, source_id, body.params)

        # 限制返回数量
        if isinstance(data, list) and len(data) > body.limit:
            data = data[:body.limit]

        return {
            'data': data,
            'total': len(data) if isinstance(data, list) else 1,
            'limited': body.limit
        }
    except ValueError as e:
        if "不存在" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"数据源预览失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"预览失败: {str(e)}")


@router.post("/{source_id}/copy", response_model=DataSourceResponse, summary="复制数据源")
async def copy_data_source(
    source_id: str,
    body: DataSourceCopyRequest,
    db: AsyncSession = Depends(get_db),
):
    """复制数据源"""
    # 检查新编码是否已存在
    if await DataSourceService.check_code_exists(db, body.new_code):
        raise HTTPException(status_code=400, detail=f"编码已存在: {body.new_code}")

    source = await DataSourceService.copy(db, source_id, body.new_code, body.new_name)
    if not source:
        raise HTTPException(status_code=404, detail="数据源不存在")
    await db.commit()
    logger.info(f"数据源已复制: {body.new_code}")
    return source


@router.post("/{source_id}/clear-cache", response_model=ResponseModel, summary="清除数据源缓存")
async def clear_data_source_cache(
    source_id: str,
    db: AsyncSession = Depends(get_db),
):
    """清除数据源缓存"""
    source = await DataSourceService.get_by_id(db, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="数据源不存在")

    await DataSourceService.clear_cache(source.code)
    return ResponseModel(message=f"缓存已清除: {source.code}")
