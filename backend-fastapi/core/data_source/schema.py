#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Data Source Schema - 数据源数据验证模式
"""
from datetime import datetime
from typing import Optional, List, Any, Dict

from pydantic import BaseModel, ConfigDict, Field


class DataSourceBase(BaseModel):
    """数据源基础Schema"""
    name: str = Field(..., description="数据源名称")
    code: str = Field(..., description="数据源编码")
    source_type: str = Field(default='static', description="数据源类型: api/sql/static")
    description: str = Field(default='', description="描述说明")
    status: bool = Field(default=True, description="是否启用")
    
    # API 配置
    api_url: str = Field(default='', description="API地址")
    api_method: str = Field(default='GET', description="请求方法")
    api_headers: Dict[str, str] = Field(default_factory=dict, description="请求头")
    api_body: Dict[str, Any] = Field(default_factory=dict, description="请求体模板")
    api_timeout: int = Field(default=30, description="超时时间")
    api_data_path: str = Field(default='', description="响应数据路径")
    
    # SQL 配置
    sql_content: str = Field(default='', description="SQL语句")
    db_connection: str = Field(default='default', description="数据库连接")
    
    # 静态数据
    static_data: List[Any] = Field(default_factory=list, description="静态数据")
    
    # 参数定义
    params: List[Dict[str, Any]] = Field(default_factory=list, description="参数定义")
    
    # 结果处理
    result_type: str = Field(default='list', description="结果类型")
    tree_config: Dict[str, Any] = Field(default_factory=dict, description="树形配置")
    field_mapping: Dict[str, str] = Field(default_factory=dict, description="字段映射")
    chart_config: Dict[str, Any] = Field(default_factory=dict, description="图表配置")
    
    # 缓存配置
    cache_enabled: bool = Field(default=False, description="是否启用缓存")
    cache_ttl: int = Field(default=300, description="缓存时间")


class DataSourceCreate(DataSourceBase):
    """数据源创建Schema"""
    pass


class DataSourceUpdate(BaseModel):
    """数据源更新Schema"""
    name: Optional[str] = None
    source_type: Optional[str] = None
    description: Optional[str] = None
    status: Optional[bool] = None
    
    api_url: Optional[str] = None
    api_method: Optional[str] = None
    api_headers: Optional[Dict[str, str]] = None
    api_body: Optional[Dict[str, Any]] = None
    api_timeout: Optional[int] = None
    api_data_path: Optional[str] = None
    
    sql_content: Optional[str] = None
    db_connection: Optional[str] = None
    
    static_data: Optional[List[Any]] = None
    params: Optional[List[Dict[str, Any]]] = None
    
    result_type: Optional[str] = None
    tree_config: Optional[Dict[str, Any]] = None
    field_mapping: Optional[Dict[str, str]] = None
    chart_config: Optional[Dict[str, Any]] = None
    
    cache_enabled: Optional[bool] = None
    cache_ttl: Optional[int] = None


class DataSourceResponse(DataSourceBase):
    """数据源响应Schema"""
    id: str
    sort: int = 0
    is_deleted: bool = False
    sys_create_datetime: Optional[datetime] = None
    sys_update_datetime: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class DataSourceSimpleOut(BaseModel):
    """数据源简单输出（用于下拉选择）"""
    id: str
    name: str
    code: str
    source_type: str
    result_type: str = "list"
    description: str = ""

    model_config = ConfigDict(from_attributes=True)


class DataSourcePreviewRequest(BaseModel):
    """数据源预览请求"""
    params: Dict[str, Any] = Field(default_factory=dict)
    limit: int = Field(default=100, ge=1, le=1000)


class DataSourceExecuteRequest(BaseModel):
    """数据源执行请求"""
    params: Dict[str, Any] = Field(default_factory=dict)


class DataSourceTestRequest(BaseModel):
    """数据源测试请求（临时配置）"""
    source_type: str
    # API 配置
    api_url: str = ""
    api_method: str = "GET"
    api_headers: Dict[str, str] = Field(default_factory=dict)
    api_body: Dict[str, Any] = Field(default_factory=dict)
    api_timeout: int = 30
    api_data_path: str = ""
    # SQL 配置
    sql_content: str = ""
    db_connection: str = "default"
    # 静态数据
    static_data: List[Any] = Field(default_factory=list)
    # 参数
    params_def: List[Dict[str, Any]] = Field(default_factory=list)
    params: Dict[str, Any] = Field(default_factory=dict)
    # 结果处理
    result_type: str = "list"
    tree_config: Dict[str, Any] = Field(default_factory=dict)
    field_mapping: Dict[str, str] = Field(default_factory=dict)
    chart_config: Dict[str, Any] = Field(default_factory=dict)


class DataSourceCopyRequest(BaseModel):
    """数据源复制请求"""
    new_code: str = Field(..., description="新编码")
    new_name: str = Field(default="", description="新名称")
