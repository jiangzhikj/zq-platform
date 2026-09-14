#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author: 臧成龙
@Contact: 939589097@qq.com
@Time: 2025-12-31
@File: loaddata.py
@Desc: 数据导入脚本 - 类似 Django 的 loaddata - 使用方法: python scripts/loaddata.py data.json
"""
"""
数据导入脚本 - 类似 Django 的 loaddata
使用方法: python scripts/loaddata.py data.json
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal, Base, engine


def auto_import_models():
    """自动导入所有模型"""
    import importlib

    project_root = Path(__file__).parent.parent

    # 需要扫描的目录
    scan_dirs = ["zq_demo", "core", "scheduler", "online_dev", "ai_platform"]

    for scan_dir in scan_dirs:
        scan_path = project_root / scan_dir
        if not scan_path.exists():
            continue

        # 递归查找所有 model.py 文件
        for model_file in scan_path.rglob("*model.py"):
            # 计算模块路径
            relative_path = model_file.relative_to(project_root)
            module_path = str(relative_path.with_suffix("")).replace("/", ".").replace("\\", ".")

            try:
                importlib.import_module(module_path)
            except ImportError as e:
                print(f"警告: 导入失败 {module_path}: {e}")


# 自动导入所有模型
auto_import_models()


def parse_value(value):
    """自动解析值类型（日期/日期时间字符串 -> date/datetime 对象）"""
    if not isinstance(value, str):
        return value

    # ISO 日期时间（如 2026-02-14T23:04:19.451515 或 2026-02-14 23:04:19）
    if len(value) >= 19 and value[4] == "-" and value[7] == "-":
        try:
            return datetime.fromisoformat(value)
        except (ValueError, TypeError):
            pass

    # 短日期（如 2025-12-28）
    if len(value) == 10 and value[4] == "-" and value[7] == "-":
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            pass

    return value


async def set_fk_checks(session: AsyncSession, disable: bool) -> bool:
    """按数据库方言切换外键约束检查。"""
    bind = session.get_bind()
    dialect_name = bind.dialect.name if bind is not None else ""

    if dialect_name == "postgresql":
        role = "replica" if disable else "origin"
        await session.execute(text(f"SET session_replication_role = '{role}'"))
        return True

    if dialect_name == "mysql":
        value = 0 if disable else 1
        await session.execute(text(f"SET FOREIGN_KEY_CHECKS = {value}"))
        return True

    if dialect_name == "sqlite":
        value = "OFF" if disable else "ON"
        await session.execute(text(f"PRAGMA foreign_keys = {value}"))
        return True

    print(f"警告: 当前数据库类型 {dialect_name}，将不会切换外键约束检查。")
    return False


async def load_data(file_path: str):
    """从 JSON 文件加载数据"""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"读取到 {len(data)} 条记录")

    # 构建模型映射
    model_map: Dict[str, Any] = {}
    for mapper in Base.registry.mappers:
        model_class = mapper.class_
        model_key = f"{model_class.__module__}.{model_class.__name__}"
        model_map[model_key] = model_class

    success_count = 0
    error_count = 0

    async with AsyncSessionLocal() as session:
        fk_checks_switched = False
        try:
            # 临时禁用外键约束（解决数据插入顺序导致的外键冲突）
            fk_checks_switched = await set_fk_checks(session=session, disable=True)

            for item in data:
                try:
                    model_name = item.get("model")
                    fields = item.get("fields", {})

                    if model_name not in model_map:
                        print(f"警告: 未找到模型 {model_name}，跳过")
                        error_count += 1
                        continue

                    model_class = model_map[model_name]

                    # 自动转换日期时间字段
                    for key, value in fields.items():
                        fields[key] = parse_value(value)

                    instance = model_class(**fields)
                    session.add(instance)
                    success_count += 1

                    # 每 100 条提交一次
                    if success_count % 100 == 0:
                        await session.commit()
                        print(f"已导入 {success_count} 条记录...")

                except Exception as e:
                    print(f"错误: 导入记录失败 - {e}")
                    print(f"  模型: {item.get('model')}")
                    print(f"  数据: {item.get('fields')}")
                    error_count += 1
                    await session.rollback()

            # 提交剩余的数据
            try:
                await session.commit()
            except Exception as e:
                print(f"提交失败: {e}")
                await session.rollback()
        finally:
            if fk_checks_switched:
                try:
                    await set_fk_checks(session=session, disable=False)
                    await session.commit()
                except Exception as e:
                    print(f"警告: 恢复外键约束失败: {e}")
                    await session.rollback()

    print("\n导入完成:")
    print(f"  成功: {success_count} 条")
    print(f"  失败: {error_count} 条")


async def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python scripts/loaddata.py <json_file>")
        sys.exit(1)

    file_path = sys.argv[1]

    if not Path(file_path).exists():
        print(f"错误: 文件不存在 - {file_path}")
        sys.exit(1)

    print(f"从文件导入数据: {file_path}")
    try:
        await load_data(file_path)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
