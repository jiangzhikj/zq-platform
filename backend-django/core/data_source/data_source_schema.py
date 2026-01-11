#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Data Source Schema - 数据源数据验证模式
"""
from typing import Optional, List, Any, Dict

from ninja import ModelSchema, Field, Schema

from common.fu_model import exclude_fields
from common.fu_schema import FuFilters
from core.data_source.data_source_model import DataSource


class DataSourceFilters(FuFilters):
    """数据源查询过滤器"""
    name: Optional[str] = Field(None, q="name__contains", alias="name")
    code: Optional[str] = Field(None, q="code__contains", alias="code")
    source_type: Optional[str] = Field(None, alias="source_type")
    status: Optional[bool] = Field(None, alias="status")


class DataSourceSchemaIn(ModelSchema):
    """数据源创建/更新输入"""

    class Config:
        model = DataSource
        model_exclude = exclude_fields


class DataSourceSchemaOut(ModelSchema):
    """数据源输出"""

    class Config:
        model = DataSource
        model_fields = "__all__"


class DataSourceSimpleOut(Schema):
    """数据源简单输出（用于下拉选择）"""
    id: str
    name: str
    code: str
    source_type: str
    result_type: str = "list"
    description: str = ""


class ParamDefinition(Schema):
    """参数定义"""
    name: str
    label: str = ""
    type: str = "string"  # string, integer, float, boolean
    required: bool = False
    default: Any = None


class DataSourcePreviewRequest(Schema):
    """数据源预览请求"""
    params: Dict[str, Any] = {}
    limit: int = 100


class DataSourceExecuteRequest(Schema):
    """数据源执行请求"""
    params: Dict[str, Any] = {}


class DataSourceTestRequest(Schema):
    """数据源测试请求（临时配置）"""
    source_type: str
    # API 配置
    api_url: str = ""
    api_method: str = "GET"
    api_headers: Dict[str, str] = {}
    api_body: Dict[str, Any] = {}
    api_timeout: int = 30
    api_data_path: str = ""
    # SQL 配置
    sql_content: str = ""
    db_connection: str = "default"
    # 静态数据
    static_data: List[Any] = []
    # 参数
    params_def: List[Dict[str, Any]] = []
    params: Dict[str, Any] = {}
    # 结果处理
    result_type: str = "list"
    tree_config: Dict[str, Any] = {}
    field_mapping: Dict[str, str] = {}


class DataSourceCopyRequest(Schema):
    """数据源复制请求"""
    new_code: str
    new_name: str = ""
