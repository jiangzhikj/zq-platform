#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Data Source API - 数据源接口

提供数据源的增删改查、执行、测试等功能
"""
import logging
from typing import List

from django.http import HttpRequest
from ninja import Router, Query
from ninja.errors import HttpError
from ninja.pagination import paginate

from common.fu_crud import create, retrieve, delete, update
from common.fu_pagination import MyPagination
from common.fu_schema import response_success
from core.data_source.data_source_model import DataSource
from core.data_source.data_source_schema import (
    DataSourceSchemaIn,
    DataSourceSchemaOut,
    DataSourceSimpleOut,
    DataSourceFilters,
    DataSourcePreviewRequest,
    DataSourceExecuteRequest,
    DataSourceTestRequest,
    DataSourceCopyRequest,
)
from core.data_source.data_source_service import DataSourceService

logger = logging.getLogger(__name__)
router = Router()


# ============ 静态路径接口（必须放在动态路径之前） ============

@router.get("/data-source", response=List[DataSourceSchemaOut], summary="获取数据源列表")
@paginate(MyPagination)
def list_data_source(request: HttpRequest, filters: DataSourceFilters = Query(...)):
    """
    获取数据源列表（分页）
    
    查询参数:
    - page: 页码
    - pageSize: 每页数量
    - name: 名称（模糊查询）
    - code: 编码（模糊查询）
    - source_type: 类型
    - status: 状态
    """
    return retrieve(request, DataSource, filters)


@router.post("/data-source", response=DataSourceSchemaOut, summary="创建数据源")
def create_data_source(request: HttpRequest, data: DataSourceSchemaIn):
    """
    创建数据源
    
    请求体:
    - name: 数据源名称 (必填)
    - code: 数据源编码 (必填，唯一)
    - source_type: 数据源类型 (api/sql/static)
    - 其他配置字段...
    """
    instance = create(request, data, DataSource)
    logger.info(f"数据源已创建: {instance.code}")
    return instance


@router.get("/data-source/get/all", response=List[DataSourceSimpleOut], summary="获取所有数据源")
def list_all_data_source(request: HttpRequest):
    """
    获取所有数据源（不分页，用于下拉选择）
    """
    return DataSource.objects.filter(is_deleted=False, status=True).values(
        'id', 'name', 'code', 'source_type', 'description'
    )


@router.post("/data-source/test", summary="测试数据源配置")
def test_data_source(request: HttpRequest, body: DataSourceTestRequest):
    """
    测试数据源配置（不保存，直接执行）
    
    请求体:
    - source_type: 数据源类型
    - 对应类型的配置字段
    - params: 测试参数
    """
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
        }

        data = DataSourceService.execute_temp(config, body.params)

        # execute_temp 已经限制了最多 100 条
        total = len(data) if isinstance(data, list) else 1

        return {
            'data': data,
            'total': total,
            'limited': DataSourceService.MAX_ROWS_TEST,
            'success': True
        }
    except ValueError as e:
        raise HttpError(400, str(e))
    except Exception as e:
        logger.error(f"数据源测试失败: {str(e)}")
        raise HttpError(500, f"测试失败: {str(e)}")


@router.get("/data-source/check-code/{code}", summary="检查编码是否可用")
def check_code_available(request: HttpRequest, code: str):
    """
    检查数据源编码是否可用
    
    路径参数:
    - code: 要检查的编码
    """
    exists = DataSource.objects.filter(code=code).exists()
    return {'available': not exists}


# ============ 动态路径接口（必须放在静态路径之后） ============

@router.get("/data-source/{source_id}", response=DataSourceSchemaOut, summary="获取数据源详情")
def get_data_source(request: HttpRequest, source_id: str):
    """
    获取数据源详情
    
    路径参数:
    - source_id: 数据源ID
    """
    return DataSource.objects.get(id=source_id)


@router.delete("/data-source/{source_id}", response=DataSourceSchemaOut, summary="删除数据源")
def delete_data_source(request: HttpRequest, source_id: str):
    """
    删除数据源
    
    路径参数:
    - source_id: 数据源ID
    """
    # 获取数据源信息用于日志
    try:
        source = DataSource.objects.get(id=source_id)
        code = source.code
    except DataSource.DoesNotExist:
        code = None

    instance = delete(source_id, DataSource)

    # 清除缓存
    if code:
        DataSourceService.clear_cache(code)
        logger.info(f"数据源已删除: {code}")

    return instance


@router.put("/data-source/{source_id}", response=DataSourceSchemaOut, summary="更新数据源")
def update_data_source(request: HttpRequest, source_id: str, data: DataSourceSchemaIn):
    """
    更新数据源
    
    路径参数:
    - source_id: 数据源ID
    
    请求体:
    - 需要更新的字段
    """
    # 获取旧的编码用于缓存清除
    try:
        old_source = DataSource.objects.get(id=source_id)
        old_code = old_source.code
    except DataSource.DoesNotExist:
        old_code = None

    instance = update(request, source_id, data, DataSource)

    # 清除缓存
    if old_code:
        DataSourceService.clear_cache(old_code)
    if instance and instance.code != old_code:
        DataSourceService.clear_cache(instance.code)

    logger.info(f"数据源已更新: {instance.code}")
    return instance


# ============ 执行接口 ============

@router.get("/data-source/execute/{code}", summary="执行数据源（GET）")
def execute_data_source_get(request: HttpRequest, code: str):
    """
    根据编码执行数据源获取数据（GET 方式）
    
    路径参数:
    - code: 数据源编码
    
    查询参数:
    - 任意参数，将传递给数据源
    """
    # 获取所有查询参数
    params = dict(request.GET)
    # 处理参数（单值转换）
    params = {k: v[0] if isinstance(v, list) and len(v) == 1 else v for k, v in params.items()}

    try:
        data = DataSourceService.execute(code, params)
        return {'data': data}
    except DataSource.DoesNotExist:
        raise HttpError(404, f"数据源不存在: {code}")
    except ValueError as e:
        raise HttpError(400, str(e))
    except Exception as e:
        logger.error(f"数据源执行失败: {str(e)}")
        raise HttpError(500, f"执行失败: {str(e)}")


@router.post("/data-source/execute/{code}", summary="执行数据源（POST）")
def execute_data_source_post(request: HttpRequest, code: str, body: DataSourceExecuteRequest):
    """
    根据编码执行数据源获取数据（POST 方式）
    
    路径参数:
    - code: 数据源编码
    
    请求体:
    - params: 参数字典
    """
    try:
        data = DataSourceService.execute(code, body.params)
        return {'data': data}
    except DataSource.DoesNotExist:
        raise HttpError(404, f"数据源不存在: {code}")
    except ValueError as e:
        raise HttpError(400, str(e))
    except Exception as e:
        logger.error(f"数据源执行失败: {str(e)}")
        raise HttpError(500, f"执行失败: {str(e)}")


# ============ 预览和测试接口 ============

@router.post("/data-source/{source_id}/preview", summary="预览数据源数据")
def preview_data_source(request: HttpRequest, source_id: str, body: DataSourcePreviewRequest):
    """
    预览数据源数据（用于调试）
    
    路径参数:
    - source_id: 数据源ID
    
    请求体:
    - params: 参数字典
    - limit: 返回数量限制（默认100）
    """
    try:
        data = DataSourceService.execute_by_id(source_id, body.params)

        # 限制返回数量
        if isinstance(data, list) and len(data) > body.limit:
            data = data[:body.limit]

        return {
            'data': data,
            'total': len(data) if isinstance(data, list) else 1,
            'limited': body.limit
        }
    except DataSource.DoesNotExist:
        raise HttpError(404, "数据源不存在")
    except ValueError as e:
        raise HttpError(400, str(e))
    except Exception as e:
        logger.error(f"数据源预览失败: {str(e)}")
        raise HttpError(500, f"预览失败: {str(e)}")


# ============ 其他接口 ============

@router.post("/data-source/{source_id}/copy", response=DataSourceSchemaOut, summary="复制数据源")
def copy_data_source(request: HttpRequest, source_id: str, body: DataSourceCopyRequest):
    """
    复制数据源
    
    路径参数:
    - source_id: 源数据源ID
    
    请求体:
    - new_code: 新编码（必填）
    - new_name: 新名称（可选，默认在原名称后加"(副本)"）
    """
    try:
        source = DataSource.objects.get(id=source_id)

        # 检查新编码是否已存在
        if DataSource.objects.filter(code=body.new_code).exists():
            raise HttpError(400, f"编码已存在: {body.new_code}")

        # 创建副本
        source.pk = None
        source.id = None
        source.code = body.new_code
        source.name = body.new_name or f"{source.name}(副本)"
        source.save()

        logger.info(f"数据源已复制: {body.new_code}")
        return source

    except DataSource.DoesNotExist:
        raise HttpError(404, "数据源不存在")


@router.post("/data-source/{source_id}/clear-cache", summary="清除数据源缓存")
def clear_data_source_cache(request: HttpRequest, source_id: str):
    """
    清除数据源缓存
    
    路径参数:
    - source_id: 数据源ID
    """
    try:
        source = DataSource.objects.get(id=source_id)
        DataSourceService.clear_cache(source.code)
        return response_success(f"缓存已清除: {source.code}")
    except DataSource.DoesNotExist:
        raise HttpError(404, "数据源不存在")
