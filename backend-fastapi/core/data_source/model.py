#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Data Source Model - 数据源模型
用于管理系统数据源配置，支持 API、SQL、静态数据等多种类型
"""
from sqlalchemy import Column, String, Text, Boolean, Integer, JSON

from app.base_model import BaseModel


class DataSource(BaseModel):
    """
    数据源模型
    
    支持三种数据源类型：
    1. API - 调用外部或内部 API 接口
    2. SQL - 执行 SQL 查询（只读）
    3. Static - 静态数据
    """
    __tablename__ = "core_data_source"

    # 所属应用（逻辑外键关联 core_application）
    application_id = Column(String(21), nullable=True, index=True, comment="所属应用ID")

    # 基本信息
    name = Column(String(100), nullable=False, comment="数据源名称")
    code = Column(String(50), unique=True, index=True, nullable=False, comment="数据源编码（唯一标识）")
    source_type = Column(String(20), default='static', comment="数据源类型: api/sql/static")
    description = Column(Text, default='', comment="描述说明")
    status = Column(Boolean, default=True, comment="是否启用")

    # ===== API 配置 =====
    api_url = Column(String(500), default='', comment="API地址，支持 {param} 占位符")
    api_method = Column(String(10), default='GET', comment="请求方法: GET/POST")
    api_headers = Column(JSON, default=dict, comment="请求头配置")
    api_body = Column(JSON, default=dict, comment="请求体模板（POST 时使用）")
    api_timeout = Column(Integer, default=30, comment="请求超时时间（秒）")
    api_data_path = Column(String(100), default='', comment="响应数据路径，如 data.list")

    # ===== SQL 配置 =====
    sql_content = Column(Text, default='', comment="SQL语句，使用 :param 作为参数占位符")
    db_connection = Column(String(50), default='default', comment="数据库连接名称")

    # ===== 静态数据 =====
    static_data = Column(JSON, default=list, comment="静态数据（JSON 数组）")

    # ===== 参数定义 =====
    params = Column(JSON, default=list, comment="参数定义列表")

    # ===== 结果处理 =====
    result_type = Column(String(20), default='list', comment="结果类型: list/tree/object/value/chart-*")
    tree_config = Column(JSON, default=dict, comment="树形转换配置")
    field_mapping = Column(JSON, default=dict, comment="字段映射配置")
    chart_config = Column(JSON, default=dict, comment="图表配置")

    # ===== 缓存配置 =====
    cache_enabled = Column(Boolean, default=False, comment="是否启用缓存")
    cache_ttl = Column(Integer, default=300, comment="缓存时间（秒）")

    def __repr__(self):
        return f"<DataSource {self.name} ({self.code})>"
