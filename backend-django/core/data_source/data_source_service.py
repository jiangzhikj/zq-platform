#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Data Source Service - 数据源服务
提供数据源执行、缓存、转换等核心功能
"""
import hashlib
import logging
import re
from typing import Any, Dict, List

import requests
from django.core.cache import cache
from django.db import connections

from core.data_source.data_source_model import DataSource

logger = logging.getLogger(__name__)


class DataSourceService:
    """数据源服务类"""

    # SQL 危险关键词（禁止执行）
    DANGEROUS_KEYWORDS = [
        'INSERT', 'UPDATE', 'DELETE', 'DROP', 'TRUNCATE',
        'ALTER', 'CREATE', 'GRANT', 'REVOKE', 'EXEC', 'EXECUTE'
    ]

    # 数据量限制
    MAX_ROWS_EXECUTE = 1000  # 正常执行最多返回 1000 条
    MAX_ROWS_TEST = 100  # 测试最多返回 100 条

    @classmethod
    def execute(cls, code: str, params: Dict[str, Any] = None) -> Any:
        """
        执行数据源获取数据
        
        Args:
            code: 数据源编码
            params: 执行参数
            
        Returns:
            处理后的数据
        """
        source = DataSource.objects.get(code=code, status=True, is_deleted=False)
        return cls.execute_source(source, params)

    @classmethod
    def execute_by_id(cls, source_id: str, params: Dict[str, Any] = None) -> Any:
        """
        根据 ID 执行数据源
        
        Args:
            source_id: 数据源 ID
            params: 执行参数
            
        Returns:
            处理后的数据
        """
        source = DataSource.objects.get(id=source_id, status=True, is_deleted=False)
        return cls.execute_source(source, params)

    @classmethod
    def execute_source(cls, source: DataSource, params: Dict[str, Any] = None) -> Any:
        """
        执行数据源对象
        
        Args:
            source: 数据源对象
            params: 执行参数
            
        Returns:
            处理后的数据
        """
        params = params or {}

        # 合并默认参数
        final_params = cls._merge_params(source.params, params)

        # 检查缓存
        if source.cache_enabled:
            cache_key = cls._get_cache_key(source.code, final_params)
            cached = cache.get(cache_key)
            if cached is not None:
                logger.debug(f"数据源 {source.code} 命中缓存")
                return cached

        # 根据类型执行
        if source.source_type == 'sql':
            result = cls._execute_sql(source, final_params)
        elif source.source_type == 'api':
            result = cls._execute_api(source, final_params)
        else:
            result = source.static_data or []

        # 字段映射
        if source.field_mapping:
            result = cls._apply_field_mapping(result, source.field_mapping)

        # 结果转换
        result = cls._transform_result(result, source)

        # 限制返回数据量
        if isinstance(result, list) and len(result) > cls.MAX_ROWS_EXECUTE:
            logger.warning(f"数据源 {source.code} 返回数据超过限制，截取前 {cls.MAX_ROWS_EXECUTE} 条")
            result = result[:cls.MAX_ROWS_EXECUTE]

        # 写入缓存
        if source.cache_enabled and source.cache_ttl > 0:
            cache_key = cls._get_cache_key(source.code, final_params)
            cache.set(cache_key, result, source.cache_ttl)
            logger.debug(f"数据源 {source.code} 结果已缓存 {source.cache_ttl}s")

        return result

    @classmethod
    def execute_temp(cls, config: Dict[str, Any], params: Dict[str, Any] = None) -> Any:
        """
        执行临时配置（用于测试/预览）
        
        Args:
            config: 临时配置字典
            params: 执行参数
            
        Returns:
            处理后的数据
        """
        params = params or {}

        # 合并默认参数
        params_def = config.get('params_def', [])
        final_params = cls._merge_params(params_def, params)

        source_type = config.get('source_type', 'static')

        # 根据类型执行
        if source_type == 'sql':
            result = cls._execute_sql_temp(config, final_params)
        elif source_type == 'api':
            result = cls._execute_api_temp(config, final_params)
        else:
            result = config.get('static_data', [])

        # 字段映射
        field_mapping = config.get('field_mapping', {})
        if field_mapping:
            result = cls._apply_field_mapping(result, field_mapping)

        # 结果转换
        result = cls._transform_result_temp(result, config)

        # 测试时限制返回数据量（最多 100 条）
        if isinstance(result, list) and len(result) > cls.MAX_ROWS_TEST:
            result = result[:cls.MAX_ROWS_TEST]

        return result

    @classmethod
    def _execute_sql(cls, source: DataSource, params: Dict[str, Any]) -> List[Dict]:
        """执行 SQL 查询"""
        sql = source.sql_content.strip()
        return cls._execute_sql_internal(sql, source.db_connection, params)

    @classmethod
    def _execute_sql_temp(cls, config: Dict[str, Any], params: Dict[str, Any]) -> List[Dict]:
        """执行临时 SQL 查询"""
        sql = config.get('sql_content', '').strip()
        db_connection = config.get('db_connection', 'default')
        return cls._execute_sql_internal(sql, db_connection, params)

    @classmethod
    def _execute_sql_internal(cls, sql: str, db_connection: str, params: Dict[str, Any]) -> List[Dict]:
        """
        内部 SQL 执行方法
        
        Args:
            sql: SQL 语句
            db_connection: 数据库连接名
            params: 参数
            
        Returns:
            查询结果列表
        """
        if not sql:
            return []

        # 安全检查：只允许 SELECT
        sql_upper = sql.upper().strip()
        if not sql_upper.startswith('SELECT') and not sql_upper.startswith('WITH'):
            raise ValueError('只允许 SELECT 或 WITH 查询')

        # 禁止危险关键词
        for keyword in cls.DANGEROUS_KEYWORDS:
            # 使用正则匹配完整单词，避免误判
            pattern = r'\b' + keyword + r'\b'
            if re.search(pattern, sql_upper):
                raise ValueError(f'SQL 中不允许使用 {keyword}')

        # 获取数据库连接
        conn = connections[db_connection]

        # 将 :param 格式转换为 %(param)s 格式（Django 风格）
        sql_formatted = re.sub(r':(\w+)', r'%(\1)s', sql)

        try:
            with conn.cursor() as cursor:
                cursor.execute(sql_formatted, params)
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()

            # 转换为字典列表
            return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            logger.error(f"SQL 执行失败: {str(e)}")
            raise ValueError(f"SQL 执行失败: {str(e)}")

    @classmethod
    def _execute_api(cls, source: DataSource, params: Dict[str, Any]) -> Any:
        """执行 API 请求"""
        return cls._execute_api_internal(
            url=source.api_url,
            method=source.api_method,
            headers=source.api_headers,
            body=source.api_body,
            timeout=source.api_timeout,
            data_path=source.api_data_path,
            params=params
        )

    @classmethod
    def _execute_api_temp(cls, config: Dict[str, Any], params: Dict[str, Any]) -> Any:
        """执行临时 API 请求"""
        return cls._execute_api_internal(
            url=config.get('api_url', ''),
            method=config.get('api_method', 'GET'),
            headers=config.get('api_headers', {}),
            body=config.get('api_body', {}),
            timeout=config.get('api_timeout', 30),
            data_path=config.get('api_data_path', ''),
            params=params
        )

    @classmethod
    def _execute_api_internal(
            cls,
            url: str,
            method: str,
            headers: Dict[str, str],
            body: Dict[str, Any],
            timeout: int,
            data_path: str,
            params: Dict[str, Any]
    ) -> Any:
        """
        内部 API 执行方法
        
        Args:
            url: API 地址
            method: 请求方法
            headers: 请求头
            body: 请求体模板
            timeout: 超时时间
            data_path: 响应数据路径
            params: 参数
            
        Returns:
            API 响应数据
        """
        if not url:
            return []

        # 替换 URL 中的参数占位符 {param}
        for key, value in params.items():
            url = url.replace(f'{{{key}}}', str(value) if value is not None else '')

        # 处理请求头中的参数
        final_headers = {}
        for k, v in headers.items():
            if isinstance(v, str):
                for pk, pv in params.items():
                    v = v.replace(f'{{{pk}}}', str(pv) if pv is not None else '')
            final_headers[k] = v

        try:
            if method.upper() == 'GET':
                # GET 请求，参数作为 query string
                resp = requests.get(url, params=params, headers=final_headers, timeout=timeout)
            else:
                # POST 请求，处理请求体
                final_body = cls._replace_params_in_dict(body.copy(), params)
                resp = requests.post(url, json=final_body, headers=final_headers, timeout=timeout)

            resp.raise_for_status()
            result = resp.json()

            # 提取数据路径
            if data_path:
                result = cls._get_nested_value(result, data_path)

            return result if result is not None else []

        except requests.RequestException as e:
            logger.error(f"API 请求失败: {str(e)}")
            raise ValueError(f"API 请求失败: {str(e)}")

    @classmethod
    def _transform_result(cls, data: Any, source: DataSource) -> Any:
        """转换结果格式"""
        return cls._transform_result_internal(
            data=data,
            result_type=source.result_type,
            tree_config=source.tree_config,
            chart_config=getattr(source, 'chart_config', {}) or {}
        )

    @classmethod
    def _transform_result_temp(cls, data: Any, config: Dict[str, Any]) -> Any:
        """转换临时结果格式"""
        return cls._transform_result_internal(
            data=data,
            result_type=config.get('result_type', 'list'),
            tree_config=config.get('tree_config', {}),
            chart_config=config.get('chart_config', {})
        )

    @classmethod
    def _transform_result_internal(
            cls,
            data: Any,
            result_type: str,
            tree_config: Dict[str, Any],
            chart_config: Dict[str, Any] = None
    ) -> Any:
        """
        内部结果转换方法
        
        Args:
            data: 原始数据
            result_type: 结果类型
            tree_config: 树形配置
            chart_config: 图表配置
            
        Returns:
            转换后的数据
        """
        if not isinstance(data, list):
            return data

        if result_type == 'tree':
            return cls._list_to_tree(
                data,
                id_field=tree_config.get('id_field', 'id'),
                parent_field=tree_config.get('parent_field', 'parent_id'),
                children_field=tree_config.get('children_field', 'children'),
                root_value=tree_config.get('root_value', None),
            )
        elif result_type == 'object':
            return data[0] if data else None
        elif result_type == 'value':
            if data and len(data) > 0:
                first_row = data[0]
                if isinstance(first_row, dict) and len(first_row) > 0:
                    return list(first_row.values())[0]
            return None
        elif result_type == 'chart-axis':
            return cls._transform_to_chart_axis(data, chart_config or {})
        elif result_type == 'chart-pie':
            return cls._transform_to_chart_pie(data, chart_config or {})
        elif result_type == 'chart-gauge':
            return cls._transform_to_chart_gauge(data, chart_config or {})
        elif result_type == 'chart-radar':
            return cls._transform_to_chart_radar(data, chart_config or {})
        elif result_type == 'chart-scatter':
            return cls._transform_to_chart_scatter(data, chart_config or {})
        elif result_type == 'chart-heatmap':
            return cls._transform_to_chart_heatmap(data, chart_config or {})

        return data

    @classmethod
    def _transform_to_chart_axis(cls, data: List[Dict], config: Dict[str, Any]) -> Dict[str, Any]:
        """
        转换为轴向图表数据格式（折线图/柱状图/面积图）
        
        输入数据格式:
        [
            {"month": "1月", "sales": 100, "profit": 50},
            {"month": "2月", "sales": 120, "profit": 60},
            ...
        ]
        
        输出数据格式:
        {
            "xAxisData": ["1月", "2月", ...],
            "seriesData": [
                {"name": "销售额", "data": [100, 120, ...]},
                {"name": "利润", "data": [50, 60, ...]}
            ]
        }
        """
        if not data:
            return {"xAxisData": [], "seriesData": []}

        x_field = config.get('x_field', '')
        series_fields = config.get('series_fields', [])
        series_names = config.get('series_names', [])

        # 如果没有配置，尝试自动推断
        if not x_field or not series_fields:
            if data and isinstance(data[0], dict):
                keys = list(data[0].keys())
                if not x_field and keys:
                    x_field = keys[0]  # 第一个字段作为 X 轴
                if not series_fields and len(keys) > 1:
                    series_fields = keys[1:]  # 其余字段作为系列

        # 提取 X 轴数据
        x_axis_data = [item.get(x_field, '') for item in data]

        # 提取系列数据
        series_data = []
        for i, field in enumerate(series_fields):
            name = series_names[i] if i < len(series_names) else field
            values = [item.get(field, 0) for item in data]
            series_data.append({
                "name": name,
                "data": values
            })

        return {
            "xAxisData": x_axis_data,
            "seriesData": series_data
        }

    @classmethod
    def _transform_to_chart_pie(cls, data: List[Dict], config: Dict[str, Any]) -> Dict[str, Any]:
        """
        转换为饼图数据格式
        
        输入数据格式:
        [
            {"category": "搜索引擎", "amount": 1048},
            {"category": "直接访问", "amount": 735},
            ...
        ]
        
        输出数据格式:
        {
            "seriesData": [
                {"name": "搜索引擎", "value": 1048},
                {"name": "直接访问", "value": 735},
                ...
            ]
        }
        """
        if not data:
            return {"seriesData": []}

        name_field = config.get('name_field', '')
        value_field = config.get('value_field', '')

        # 如果没有配置，尝试自动推断
        if not name_field or not value_field:
            if data and isinstance(data[0], dict):
                keys = list(data[0].keys())
                if len(keys) >= 2:
                    # 假设第一个是名称，第二个是数值
                    if not name_field:
                        name_field = keys[0]
                    if not value_field:
                        value_field = keys[1]

        # 转换数据
        series_data = []
        for item in data:
            name = item.get(name_field, '')
            value = item.get(value_field, 0)
            series_data.append({
                "name": name,
                "value": value
            })

        return {
            "seriesData": series_data
        }

    @classmethod
    def _transform_to_chart_gauge(cls, data: List[Dict], config: Dict[str, Any]) -> Dict[str, Any]:
        """
        转换为仪表盘数据格式
        
        输入数据格式:
        [{"value": 75, "name": "完成率", "max": 100}]
        
        输出数据格式:
        {
            "value": 75,
            "name": "完成率",
            "max": 100
        }
        """
        if not data:
            return {"value": 0, "name": "", "max": 100}

        value_field = config.get('value_field', 'value')
        name_field = config.get('name_field', 'name')
        max_field = config.get('max_field', 'max')

        first_row = data[0] if data else {}

        return {
            "value": first_row.get(value_field, 0),
            "name": first_row.get(name_field, ''),
            "max": first_row.get(max_field, 100)
        }

    @classmethod
    def _transform_to_chart_radar(cls, data: List[Dict], config: Dict[str, Any]) -> Dict[str, Any]:
        """
        转换为雷达图数据格式
        
        输入数据格式:
        [
            {"name": "销售", "max": 100, "budget": 80, "actual": 90},
            {"name": "管理", "max": 100, "budget": 70, "actual": 85},
            ...
        ]
        
        输出数据格式:
        {
            "indicator": [
                {"name": "销售", "max": 100},
                {"name": "管理", "max": 100},
                ...
            ],
            "seriesData": [
                {"name": "预算", "value": [80, 70, ...]},
                {"name": "实际", "value": [90, 85, ...]}
            ]
        }
        """
        if not data:
            return {"indicator": [], "seriesData": []}

        indicator_field = config.get('indicator_field', 'name')
        max_field = config.get('max_field', 'max')
        value_fields = config.get('value_fields', [])
        series_names = config.get('series_names', [])

        # 如果没有配置 value_fields，自动推断
        if not value_fields and data:
            keys = list(data[0].keys())
            value_fields = [k for k in keys if k not in [indicator_field, max_field]]

        # 构建指标
        indicator = []
        for item in data:
            indicator.append({
                "name": item.get(indicator_field, ''),
                "max": item.get(max_field, 100)
            })

        # 构建系列数据
        series_data = []
        for i, field in enumerate(value_fields):
            name = series_names[i] if i < len(series_names) else field
            values = [item.get(field, 0) for item in data]
            series_data.append({
                "name": name,
                "value": values
            })

        return {
            "indicator": indicator,
            "seriesData": series_data
        }

    @classmethod
    def _transform_to_chart_scatter(cls, data: List[Dict], config: Dict[str, Any]) -> Dict[str, Any]:
        """
        转换为散点图数据格式
        
        输入数据格式:
        [
            {"x": 10, "y": 20, "size": 5, "name": "A"},
            {"x": 15, "y": 25, "size": 8, "name": "B"},
            ...
        ]
        
        输出数据格式:
        {
            "seriesData": [
                [10, 20, 5, "A"],
                [15, 25, 8, "B"],
                ...
            ]
        }
        """
        if not data:
            return {"seriesData": []}

        x_field = config.get('x_field', 'x')
        y_field = config.get('y_field', 'y')
        size_field = config.get('size_field', '')
        name_field = config.get('name_field', '')

        series_data = []
        for item in data:
            point = [item.get(x_field, 0), item.get(y_field, 0)]
            if size_field:
                point.append(item.get(size_field, 0))
            if name_field:
                point.append(item.get(name_field, ''))
            series_data.append(point)

        return {
            "seriesData": series_data
        }

    @classmethod
    def _transform_to_chart_heatmap(cls, data: List[Dict], config: Dict[str, Any]) -> Dict[str, Any]:
        """
        转换为热力图数据格式
        
        输入数据格式:
        [
            {"x": "周一", "y": "上午", "value": 10},
            {"x": "周一", "y": "下午", "value": 20},
            ...
        ]
        
        输出数据格式:
        {
            "xAxisData": ["周一", "周二", ...],
            "yAxisData": ["上午", "下午", ...],
            "seriesData": [[0, 0, 10], [0, 1, 20], ...]  # [x索引, y索引, 值]
        }
        """
        if not data:
            return {"xAxisData": [], "yAxisData": [], "seriesData": []}

        x_field = config.get('x_field', 'x')
        y_field = config.get('y_field', 'y')
        value_field = config.get('value_field', 'value')

        # 提取唯一的 x 和 y 值
        x_values = list(dict.fromkeys(item.get(x_field, '') for item in data))
        y_values = list(dict.fromkeys(item.get(y_field, '') for item in data))

        # 创建索引映射
        x_index = {v: i for i, v in enumerate(x_values)}
        y_index = {v: i for i, v in enumerate(y_values)}

        # 构建数据
        series_data = []
        for item in data:
            x = item.get(x_field, '')
            y = item.get(y_field, '')
            value = item.get(value_field, 0)
            series_data.append([x_index.get(x, 0), y_index.get(y, 0), value])

        return {
            "xAxisData": x_values,
            "yAxisData": y_values,
            "seriesData": series_data
        }

    @classmethod
    def _list_to_tree(
            cls,
            data: List[Dict],
            id_field: str,
            parent_field: str,
            children_field: str,
            root_value: Any = None
    ) -> List[Dict]:
        """
        列表转树形结构
        
        Args:
            data: 列表数据
            id_field: ID 字段名
            parent_field: 父级 ID 字段名
            children_field: 子节点字段名
            root_value: 根节点的父级 ID 值
            
        Returns:
            树形结构数据
        """
        if not data:
            return []

        # 创建 ID 到节点的映射
        mapping = {}
        for item in data:
            item_id = item.get(id_field)
            if item_id is not None:
                mapping[item_id] = {**item, children_field: []}

        # 构建树
        tree = []
        for item in data:
            item_id = item.get(id_field)
            parent_id = item.get(parent_field)
            node = mapping.get(item_id)

            if node is None:
                continue

            # 判断是否为根节点
            is_root = (
                    parent_id is None or
                    parent_id == root_value or
                    parent_id == '' or
                    parent_id not in mapping
            )

            if is_root:
                tree.append(node)
            else:
                parent_node = mapping.get(parent_id)
                if parent_node:
                    parent_node[children_field].append(node)

        return tree

    @classmethod
    def _apply_field_mapping(cls, data: List[Dict], mapping: Dict[str, str]) -> List[Dict]:
        """
        应用字段映射
        
        Args:
            data: 原始数据列表
            mapping: 字段映射 {原字段: 新字段}
            
        Returns:
            映射后的数据
        """
        if not data or not mapping:
            return data

        result = []
        for item in data:
            if not isinstance(item, dict):
                result.append(item)
                continue

            new_item = {}
            # 先添加映射的字段
            for old_key, new_key in mapping.items():
                if old_key in item:
                    new_item[new_key] = item[old_key]
            # 保留未映射的字段
            for key, value in item.items():
                if key not in mapping:
                    new_item[key] = value
            result.append(new_item)

        return result

    @classmethod
    def _merge_params(cls, param_defs: List[Dict], input_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        合并参数（应用默认值和类型转换）
        
        Args:
            param_defs: 参数定义列表
            input_params: 输入参数
            
        Returns:
            合并后的参数
        """
        result = {}

        for p in param_defs:
            name = p.get('name')
            if not name:
                continue

            param_type = p.get('type', 'string')
            required = p.get('required', False)
            default = p.get('default')

            if name in input_params:
                value = input_params[name]
                # 类型转换
                result[name] = cls._convert_param_type(value, param_type)
            elif default is not None:
                result[name] = default
            elif required:
                raise ValueError(f"缺少必填参数: {name}")
            else:
                result[name] = None

        # 添加未定义但传入的参数
        for key, value in input_params.items():
            if key not in result:
                result[key] = value

        return result

    @classmethod
    def _convert_param_type(cls, value: Any, param_type: str) -> Any:
        """
        参数类型转换
        
        Args:
            value: 原始值
            param_type: 目标类型
            
        Returns:
            转换后的值
        """
        if value is None:
            return None

        try:
            if param_type == 'integer':
                return int(value)
            elif param_type == 'float':
                return float(value)
            elif param_type == 'boolean':
                if isinstance(value, bool):
                    return value
                return str(value).lower() in ('true', '1', 'yes')
            else:
                return str(value)
        except (ValueError, TypeError):
            return value

    @classmethod
    def _replace_params_in_dict(cls, data: Dict, params: Dict[str, Any]) -> Dict:
        """
        递归替换字典中的参数占位符
        
        Args:
            data: 原始字典
            params: 参数
            
        Returns:
            替换后的字典
        """
        result = {}
        for key, value in data.items():
            if isinstance(value, str):
                for pk, pv in params.items():
                    value = value.replace(f'{{{pk}}}', str(pv) if pv is not None else '')
                result[key] = value
            elif isinstance(value, dict):
                result[key] = cls._replace_params_in_dict(value, params)
            elif isinstance(value, list):
                result[key] = [
                    cls._replace_params_in_dict(item, params) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                result[key] = value
        return result

    @classmethod
    def _get_nested_value(cls, data: Any, path: str) -> Any:
        """
        获取嵌套字典中的值
        
        Args:
            data: 数据
            path: 路径，如 "data.list"
            
        Returns:
            对应路径的值
        """
        if not path:
            return data

        keys = path.split('.')
        result = data

        for key in keys:
            if isinstance(result, dict):
                result = result.get(key)
            elif isinstance(result, list) and key.isdigit():
                index = int(key)
                result = result[index] if 0 <= index < len(result) else None
            else:
                return None

            if result is None:
                return None

        return result

    @classmethod
    def _get_cache_key(cls, code: str, params: Dict[str, Any]) -> str:
        """
        生成缓存键
        
        Args:
            code: 数据源编码
            params: 参数
            
        Returns:
            缓存键
        """
        params_str = str(sorted(params.items()))
        params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]
        return f"datasource:{code}:{params_hash}"

    @classmethod
    def clear_cache(cls, code: str) -> None:
        """
        清除数据源缓存
        
        Args:
            code: 数据源编码
        """
        # 由于参数组合可能很多，这里使用模式匹配删除
        # 注意：这需要 Redis 后端支持
        pattern = f"datasource:{code}:*"
        try:
            from django_redis import get_redis_connection
            redis_conn = get_redis_connection("default")
            keys = redis_conn.keys(pattern)
            if keys:
                redis_conn.delete(*keys)
                logger.info(f"已清除数据源 {code} 的 {len(keys)} 个缓存")
        except Exception as e:
            logger.warning(f"清除缓存失败: {str(e)}")
