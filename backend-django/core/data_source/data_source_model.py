#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Data Source Model - 数据源模型
用于管理系统数据源配置，支持 API、SQL、静态数据等多种类型
"""
from django.db import models

from common.fu_model import RootModel

# 数据源类型选项
SOURCE_TYPE_CHOICES = [
    ('api', 'API接口'),
    ('sql', 'SQL查询'),
    ('static', '静态数据'),
]

# 请求方法选项
HTTP_METHOD_CHOICES = [
    ('GET', 'GET'),
    ('POST', 'POST'),
]

# 结果类型选项
RESULT_TYPE_CHOICES = [
    ('list', '列表'),
    ('tree', '树形'),
    ('object', '单对象'),
    ('value', '单值'),
    ('chart-axis', '轴向图表'),  # 折线图/柱状图/面积图
    ('chart-pie', '饼图数据'),  # 饼图/漏斗图
    ('chart-gauge', '仪表盘'),  # 仪表盘/进度图
    ('chart-radar', '雷达图'),  # 雷达图
    ('chart-scatter', '散点图'),  # 散点图/气泡图
    ('chart-heatmap', '热力图'),  # 热力图
]


class DataSource(RootModel):
    """
    数据源模型
    
    支持三种数据源类型：
    1. API - 调用外部或内部 API 接口
    2. SQL - 执行 SQL 查询（只读）
    3. Static - 静态数据
    """

    # 基本信息
    name = models.CharField(
        max_length=100,
        help_text="数据源名称"
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="数据源编码（唯一标识）"
    )
    source_type = models.CharField(
        max_length=20,
        choices=SOURCE_TYPE_CHOICES,
        default='static',
        help_text="数据源类型"
    )
    description = models.TextField(
        blank=True,
        default='',
        help_text="描述说明"
    )
    status = models.BooleanField(
        default=True,
        help_text="是否启用"
    )

    # ===== API 配置 =====
    api_url = models.CharField(
        max_length=500,
        blank=True,
        default='',
        help_text="API地址，支持 {param} 占位符"
    )
    api_method = models.CharField(
        max_length=10,
        choices=HTTP_METHOD_CHOICES,
        default='GET',
        help_text="请求方法"
    )
    api_headers = models.JSONField(
        default=dict,
        blank=True,
        help_text="请求头配置"
    )
    api_body = models.JSONField(
        default=dict,
        blank=True,
        help_text="请求体模板（POST 时使用）"
    )
    api_timeout = models.IntegerField(
        default=30,
        help_text="请求超时时间（秒）"
    )
    # API 响应数据路径，如 data.list
    api_data_path = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text="响应数据路径，如 data.list"
    )

    # ===== SQL 配置 =====
    sql_content = models.TextField(
        blank=True,
        default='',
        help_text="SQL语句，使用 :param 作为参数占位符"
    )
    db_connection = models.CharField(
        max_length=50,
        default='default',
        help_text="数据库连接名称"
    )

    # ===== 静态数据 =====
    static_data = models.JSONField(
        default=list,
        blank=True,
        help_text="静态数据（JSON 数组）"
    )

    # ===== 参数定义 =====
    params = models.JSONField(
        default=list,
        blank=True,
        help_text="""参数定义列表，格式：
        [
            {
                "name": "status",
                "label": "状态",
                "type": "integer",  # string, integer, float, boolean
                "required": false,
                "default": 1
            }
        ]"""
    )

    # ===== 结果处理 =====
    result_type = models.CharField(
        max_length=20,
        choices=RESULT_TYPE_CHOICES,
        default='list',
        help_text="结果类型"
    )

    # 树形转换配置
    tree_config = models.JSONField(
        default=dict,
        blank=True,
        help_text="""树形转换配置，格式：
        {
            "id_field": "id",
            "parent_field": "parent_id",
            "children_field": "children",
            "root_value": null  # 根节点的 parent_id 值
        }"""
    )

    # 字段映射
    field_mapping = models.JSONField(
        default=dict,
        blank=True,
        help_text="""字段映射配置，格式：
        {
            "id": "value",
            "name": "label"
        }"""
    )

    # 图表配置（图表类型使用）
    chart_config = models.JSONField(
        default=dict,
        blank=True,
        help_text="""图表配置，格式：
        chart-axis（轴向图表）:
        {
            "x_field": "month",                    # X轴字段
            "series_fields": ["sales", "profit"], # 系列字段（多个）
            "series_names": ["销售额", "利润"]     # 系列名称（可选）
        }
        
        chart-pie（饼图数据）:
        {
            "name_field": "category",   # 名称字段
            "value_field": "amount"     # 数值字段
        }
        
        chart-gauge（仪表盘）:
        {
            "value_field": "value",     # 数值字段
            "name_field": "name",       # 名称字段（可选）
            "max_field": "max"          # 最大值字段（可选）
        }
        
        chart-radar（雷达图）:
        {
            "indicator_field": "name",  # 指标名称字段
            "max_field": "max",         # 指标最大值字段
            "value_fields": ["value1", "value2"],  # 数值字段（多个系列）
            "series_names": ["预算", "实际"]        # 系列名称（可选）
        }
        
        chart-scatter（散点图）:
        {
            "x_field": "x",             # X坐标字段
            "y_field": "y",             # Y坐标字段
            "size_field": "size",       # 大小字段（可选，气泡图）
            "name_field": "name"        # 名称字段（可选）
        }
        
        chart-heatmap（热力图）:
        {
            "x_field": "x",             # X坐标字段
            "y_field": "y",             # Y坐标字段
            "value_field": "value"      # 数值字段
        }"""
    )

    # ===== 缓存配置 =====
    cache_enabled = models.BooleanField(
        default=False,
        help_text="是否启用缓存"
    )
    cache_ttl = models.IntegerField(
        default=300,
        help_text="缓存时间（秒）"
    )

    class Meta:
        db_table = 'core_data_source'
        verbose_name = '数据源'
        verbose_name_plural = verbose_name
        ordering = ['-sort', '-sys_create_datetime']

    def __str__(self):
        return f"{self.name} ({self.code})"
