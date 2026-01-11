#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Data Source Service - 数据源服务
提供数据源执行、缓存、转换等核心功能（异步版本）
"""
import hashlib
import logging
import re
from typing import Any, Dict, List, Optional, Tuple

import httpx
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from utils.redis import RedisClient
from core.data_source.model import DataSource

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

    # ==================== CRUD 方法 ====================

    @classmethod
    async def get_list(
        cls,
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        name: str = None,
        code: str = None,
        source_type: str = None,
        status: bool = None,
    ) -> Tuple[List[DataSource], int]:
        """获取数据源列表"""
        stmt = select(DataSource).where(DataSource.is_deleted == False)

        if name:
            stmt = stmt.where(DataSource.name.contains(name))
        if code:
            stmt = stmt.where(DataSource.code.contains(code))
        if source_type:
            stmt = stmt.where(DataSource.source_type == source_type)
        if status is not None:
            stmt = stmt.where(DataSource.status == status)

        # 计算总数
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await db.execute(count_stmt)
        total = total_result.scalar() or 0

        # 分页
        stmt = stmt.order_by(DataSource.sort.desc(), DataSource.sys_create_datetime.desc())
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)

        result = await db.execute(stmt)
        items = list(result.scalars().all())

        return items, total

    @classmethod
    async def get_all(cls, db: AsyncSession) -> List[DataSource]:
        """获取所有启用的数据源"""
        stmt = select(DataSource).where(
            DataSource.is_deleted == False,
            DataSource.status == True,
        ).order_by(DataSource.sort.desc())
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @classmethod
    async def get_by_id(cls, db: AsyncSession, source_id: str) -> Optional[DataSource]:
        """根据ID获取数据源"""
        stmt = select(DataSource).where(
            DataSource.id == source_id,
            DataSource.is_deleted == False,
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @classmethod
    async def get_by_code(cls, db: AsyncSession, code: str) -> Optional[DataSource]:
        """根据编码获取数据源"""
        stmt = select(DataSource).where(
            DataSource.code == code,
            DataSource.is_deleted == False,
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @classmethod
    async def create(cls, db: AsyncSession, data: dict) -> DataSource:
        """创建数据源"""
        source = DataSource(**data)
        db.add(source)
        await db.flush()
        await db.refresh(source)
        return source

    @classmethod
    async def update(cls, db: AsyncSession, source_id: str, data: dict) -> Optional[DataSource]:
        """更新数据源"""
        source = await cls.get_by_id(db, source_id)
        if not source:
            return None

        old_code = source.code
        for key, value in data.items():
            if value is not None and hasattr(source, key):
                setattr(source, key, value)

        db.add(source)
        await db.flush()
        await db.refresh(source)

        # 清除缓存
        await cls.clear_cache(old_code)
        if source.code != old_code:
            await cls.clear_cache(source.code)

        return source

    @classmethod
    async def delete(cls, db: AsyncSession, source_id: str) -> bool:
        """删除数据源（软删除）"""
        source = await cls.get_by_id(db, source_id)
        if not source:
            return False

        source.is_deleted = True
        db.add(source)
        await db.flush()

        # 清除缓存
        await cls.clear_cache(source.code)
        return True

    @classmethod
    async def check_code_exists(cls, db: AsyncSession, code: str, exclude_id: str = None) -> bool:
        """检查编码是否存在"""
        stmt = select(DataSource).where(DataSource.code == code)
        if exclude_id:
            stmt = stmt.where(DataSource.id != exclude_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none() is not None

    @classmethod
    async def copy(cls, db: AsyncSession, source_id: str, new_code: str, new_name: str = None) -> Optional[DataSource]:
        """复制数据源"""
        source = await cls.get_by_id(db, source_id)
        if not source:
            return None

        # 创建副本
        new_source = DataSource(
            name=new_name or f"{source.name}(副本)",
            code=new_code,
            source_type=source.source_type,
            description=source.description,
            status=source.status,
            api_url=source.api_url,
            api_method=source.api_method,
            api_headers=source.api_headers,
            api_body=source.api_body,
            api_timeout=source.api_timeout,
            api_data_path=source.api_data_path,
            sql_content=source.sql_content,
            db_connection=source.db_connection,
            static_data=source.static_data,
            params=source.params,
            result_type=source.result_type,
            tree_config=source.tree_config,
            field_mapping=source.field_mapping,
            chart_config=source.chart_config,
            cache_enabled=source.cache_enabled,
            cache_ttl=source.cache_ttl,
        )
        db.add(new_source)
        await db.flush()
        await db.refresh(new_source)
        return new_source

    # ==================== 执行方法 ====================

    @classmethod
    async def execute(cls, db: AsyncSession, code: str, params: Dict[str, Any] = None) -> Any:
        """根据编码执行数据源"""
        source = await cls.get_by_code(db, code)
        if not source or not source.status:
            raise ValueError(f"数据源不存在或已禁用: {code}")
        return await cls.execute_source(db, source, params)

    @classmethod
    async def execute_by_id(cls, db: AsyncSession, source_id: str, params: Dict[str, Any] = None) -> Any:
        """根据ID执行数据源"""
        source = await cls.get_by_id(db, source_id)
        if not source or not source.status:
            raise ValueError("数据源不存在或已禁用")
        return await cls.execute_source(db, source, params)

    @classmethod
    async def execute_source(cls, db: AsyncSession, source: DataSource, params: Dict[str, Any] = None) -> Any:
        """执行数据源对象"""
        params = params or {}

        # 合并默认参数
        final_params = cls._merge_params(source.params or [], params)

        # 检查缓存
        if source.cache_enabled:
            cache_key = cls._get_cache_key(source.code, final_params)
            cached = await cls._get_cache(cache_key)
            if cached is not None:
                logger.debug(f"数据源 {source.code} 命中缓存")
                return cached

        # 根据类型执行
        if source.source_type == 'sql':
            result = await cls._execute_sql(db, source, final_params)
        elif source.source_type == 'api':
            result = await cls._execute_api(source, final_params)
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
            await cls._set_cache(cache_key, result, source.cache_ttl)
            logger.debug(f"数据源 {source.code} 结果已缓存 {source.cache_ttl}s")

        return result

    @classmethod
    async def execute_temp(cls, db: AsyncSession, config: Dict[str, Any], params: Dict[str, Any] = None) -> Any:
        """执行临时配置（用于测试/预览）"""
        params = params or {}

        # 合并默认参数
        params_def = config.get('params_def', [])
        final_params = cls._merge_params(params_def, params)

        source_type = config.get('source_type', 'static')

        # 根据类型执行
        if source_type == 'sql':
            result = await cls._execute_sql_temp(db, config, final_params)
        elif source_type == 'api':
            result = await cls._execute_api_temp(config, final_params)
        else:
            result = config.get('static_data', [])

        # 字段映射
        field_mapping = config.get('field_mapping', {})
        if field_mapping:
            result = cls._apply_field_mapping(result, field_mapping)

        # 结果转换
        result = cls._transform_result_temp(result, config)

        # 测试时限制返回数据量
        if isinstance(result, list) and len(result) > cls.MAX_ROWS_TEST:
            result = result[:cls.MAX_ROWS_TEST]

        return result

    # ==================== SQL 执行 ====================

    @classmethod
    async def _execute_sql(cls, db: AsyncSession, source: DataSource, params: Dict[str, Any]) -> List[Dict]:
        """执行 SQL 查询"""
        sql = (source.sql_content or '').strip()
        return await cls._execute_sql_internal(db, sql, params)

    @classmethod
    async def _execute_sql_temp(cls, db: AsyncSession, config: Dict[str, Any], params: Dict[str, Any]) -> List[Dict]:
        """执行临时 SQL 查询"""
        sql = config.get('sql_content', '').strip()
        return await cls._execute_sql_internal(db, sql, params)

    @classmethod
    async def _execute_sql_internal(cls, db: AsyncSession, sql: str, params: Dict[str, Any]) -> List[Dict]:
        """内部 SQL 执行方法"""
        if not sql:
            return []

        # 安全检查：只允许 SELECT
        sql_upper = sql.upper().strip()
        if not sql_upper.startswith('SELECT') and not sql_upper.startswith('WITH'):
            raise ValueError('只允许 SELECT 或 WITH 查询')

        # 禁止危险关键词
        for keyword in cls.DANGEROUS_KEYWORDS:
            pattern = r'\b' + keyword + r'\b'
            if re.search(pattern, sql_upper):
                raise ValueError(f'SQL 中不允许使用 {keyword}')

        # 将 :param 格式转换为 SQLAlchemy 格式
        from sqlalchemy import text
        try:
            result = await db.execute(text(sql), params)
            rows = result.fetchall()
            columns = result.keys()
            return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            logger.error(f"SQL 执行失败: {str(e)}")
            raise ValueError(f"SQL 执行失败: {str(e)}")

    # ==================== API 执行 ====================

    @classmethod
    async def _execute_api(cls, source: DataSource, params: Dict[str, Any]) -> Any:
        """执行 API 请求"""
        return await cls._execute_api_internal(
            url=source.api_url or '',
            method=source.api_method or 'GET',
            headers=source.api_headers or {},
            body=source.api_body or {},
            timeout=source.api_timeout or 30,
            data_path=source.api_data_path or '',
            params=params
        )

    @classmethod
    async def _execute_api_temp(cls, config: Dict[str, Any], params: Dict[str, Any]) -> Any:
        """执行临时 API 请求"""
        return await cls._execute_api_internal(
            url=config.get('api_url', ''),
            method=config.get('api_method', 'GET'),
            headers=config.get('api_headers', {}),
            body=config.get('api_body', {}),
            timeout=config.get('api_timeout', 30),
            data_path=config.get('api_data_path', ''),
            params=params
        )

    @classmethod
    async def _execute_api_internal(
            cls,
            url: str,
            method: str,
            headers: Dict[str, str],
            body: Dict[str, Any],
            timeout: int,
            data_path: str,
            params: Dict[str, Any]
    ) -> Any:
        """内部 API 执行方法"""
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
            async with httpx.AsyncClient(timeout=timeout) as client:
                if method.upper() == 'GET':
                    resp = await client.get(url, params=params, headers=final_headers)
                else:
                    final_body = cls._replace_params_in_dict(body.copy(), params)
                    resp = await client.post(url, json=final_body, headers=final_headers)

                resp.raise_for_status()
                result = resp.json()

                # 提取数据路径
                if data_path:
                    result = cls._get_nested_value(result, data_path)

                return result if result is not None else []

        except httpx.RequestError as e:
            logger.error(f"API 请求失败: {str(e)}")
            raise ValueError(f"API 请求失败: {str(e)}")

    # ==================== 结果转换 ====================

    @classmethod
    def _transform_result(cls, data: Any, source: DataSource) -> Any:
        """转换结果格式"""
        return cls._transform_result_internal(
            data=data,
            result_type=source.result_type or 'list',
            tree_config=source.tree_config or {},
            chart_config=source.chart_config or {}
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
        """内部结果转换方法"""
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
        """转换为轴向图表数据格式"""
        if not data:
            return {"xAxisData": [], "seriesData": []}

        x_field = config.get('x_field', '')
        series_fields = config.get('series_fields', [])
        series_names = config.get('series_names', [])

        if not x_field or not series_fields:
            if data and isinstance(data[0], dict):
                keys = list(data[0].keys())
                if not x_field and keys:
                    x_field = keys[0]
                if not series_fields and len(keys) > 1:
                    series_fields = keys[1:]

        x_axis_data = [item.get(x_field, '') for item in data]

        series_data = []
        for i, field in enumerate(series_fields):
            name = series_names[i] if i < len(series_names) else field
            values = [item.get(field, 0) for item in data]
            series_data.append({"name": name, "data": values})

        return {"xAxisData": x_axis_data, "seriesData": series_data}

    @classmethod
    def _transform_to_chart_pie(cls, data: List[Dict], config: Dict[str, Any]) -> Dict[str, Any]:
        """转换为饼图数据格式"""
        if not data:
            return {"seriesData": []}

        name_field = config.get('name_field', '')
        value_field = config.get('value_field', '')

        if not name_field or not value_field:
            if data and isinstance(data[0], dict):
                keys = list(data[0].keys())
                if len(keys) >= 2:
                    if not name_field:
                        name_field = keys[0]
                    if not value_field:
                        value_field = keys[1]

        series_data = []
        for item in data:
            series_data.append({
                "name": item.get(name_field, ''),
                "value": item.get(value_field, 0)
            })

        return {"seriesData": series_data}

    @classmethod
    def _transform_to_chart_gauge(cls, data: List[Dict], config: Dict[str, Any]) -> Dict[str, Any]:
        """转换为仪表盘数据格式"""
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
        """转换为雷达图数据格式"""
        if not data:
            return {"indicator": [], "seriesData": []}

        indicator_field = config.get('indicator_field', 'name')
        max_field = config.get('max_field', 'max')
        value_fields = config.get('value_fields', [])
        series_names = config.get('series_names', [])

        if not value_fields and data:
            keys = list(data[0].keys())
            value_fields = [k for k in keys if k not in [indicator_field, max_field]]

        indicator = []
        for item in data:
            indicator.append({
                "name": item.get(indicator_field, ''),
                "max": item.get(max_field, 100)
            })

        series_data = []
        for i, field in enumerate(value_fields):
            name = series_names[i] if i < len(series_names) else field
            values = [item.get(field, 0) for item in data]
            series_data.append({"name": name, "value": values})

        return {"indicator": indicator, "seriesData": series_data}

    @classmethod
    def _transform_to_chart_scatter(cls, data: List[Dict], config: Dict[str, Any]) -> Dict[str, Any]:
        """转换为散点图数据格式"""
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

        return {"seriesData": series_data}

    @classmethod
    def _transform_to_chart_heatmap(cls, data: List[Dict], config: Dict[str, Any]) -> Dict[str, Any]:
        """转换为热力图数据格式"""
        if not data:
            return {"xAxisData": [], "yAxisData": [], "seriesData": []}

        x_field = config.get('x_field', 'x')
        y_field = config.get('y_field', 'y')
        value_field = config.get('value_field', 'value')

        x_values = list(dict.fromkeys(item.get(x_field, '') for item in data))
        y_values = list(dict.fromkeys(item.get(y_field, '') for item in data))

        x_index = {v: i for i, v in enumerate(x_values)}
        y_index = {v: i for i, v in enumerate(y_values)}

        series_data = []
        for item in data:
            x = item.get(x_field, '')
            y = item.get(y_field, '')
            value = item.get(value_field, 0)
            series_data.append([x_index.get(x, 0), y_index.get(y, 0), value])

        return {"xAxisData": x_values, "yAxisData": y_values, "seriesData": series_data}

    @classmethod
    def _list_to_tree(
            cls,
            data: List[Dict],
            id_field: str,
            parent_field: str,
            children_field: str,
            root_value: Any = None
    ) -> List[Dict]:
        """列表转树形结构"""
        if not data:
            return []

        mapping = {}
        for item in data:
            item_id = item.get(id_field)
            if item_id is not None:
                mapping[item_id] = {**item, children_field: []}

        tree = []
        for item in data:
            item_id = item.get(id_field)
            parent_id = item.get(parent_field)
            node = mapping.get(item_id)

            if node is None:
                continue

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

    # ==================== 工具方法 ====================

    @classmethod
    def _apply_field_mapping(cls, data: List[Dict], mapping: Dict[str, str]) -> List[Dict]:
        """应用字段映射"""
        if not data or not mapping:
            return data

        result = []
        for item in data:
            if not isinstance(item, dict):
                result.append(item)
                continue

            new_item = {}
            for old_key, new_key in mapping.items():
                if old_key in item:
                    new_item[new_key] = item[old_key]
            for key, value in item.items():
                if key not in mapping:
                    new_item[key] = value
            result.append(new_item)

        return result

    @classmethod
    def _merge_params(cls, param_defs: List[Dict], input_params: Dict[str, Any]) -> Dict[str, Any]:
        """合并参数"""
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
                result[name] = cls._convert_param_type(value, param_type)
            elif default is not None:
                result[name] = default
            elif required:
                raise ValueError(f"缺少必填参数: {name}")
            else:
                result[name] = None

        for key, value in input_params.items():
            if key not in result:
                result[key] = value

        return result

    @classmethod
    def _convert_param_type(cls, value: Any, param_type: str) -> Any:
        """参数类型转换"""
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
        """递归替换字典中的参数占位符"""
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
        """获取嵌套字典中的值"""
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

    # ==================== 缓存方法 ====================

    @classmethod
    def _get_cache_key(cls, code: str, params: Dict[str, Any]) -> str:
        """生成缓存键"""
        params_str = str(sorted(params.items()))
        params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]
        return f"datasource:{code}:{params_hash}"

    @classmethod
    async def _get_cache(cls, key: str) -> Any:
        """获取缓存"""
        try:
            import json
            client = await RedisClient.get_client()
            value = await client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.warning(f"获取缓存失败: {str(e)}")
            return None

    @classmethod
    async def _set_cache(cls, key: str, value: Any, ttl: int) -> None:
        """设置缓存"""
        try:
            import json
            client = await RedisClient.get_client()
            await client.set(key, json.dumps(value, default=str), ex=ttl)
        except Exception as e:
            logger.warning(f"设置缓存失败: {str(e)}")

    @classmethod
    async def clear_cache(cls, code: str) -> None:
        """清除数据源缓存"""
        pattern = f"datasource:{code}:*"
        try:
            client = await RedisClient.get_client()
            keys = []
            async for key in client.scan_iter(match=pattern):
                keys.append(key)
            if keys:
                await client.delete(*keys)
                logger.info(f"已清除数据源 {code} 的 {len(keys)} 个缓存")
        except Exception as e:
            logger.warning(f"清除缓存失败: {str(e)}")
