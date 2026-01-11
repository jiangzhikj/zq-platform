#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
页面管理 Schema 定义
"""
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, ConfigDict


# ============ 页面元数据 Schema ============

class PageMetaBase(BaseModel):
    """页面基础信息"""
    name: str = Field(..., description="页面名称")
    code: str = Field(..., description="页面编码")
    category: str = Field("", description="分类")
    description: str = Field("", description="描述")
    sort: int = Field(0, description="排序")


class PageMetaCreateIn(PageMetaBase):
    """创建页面请求"""
    page_config: Dict[str, Any] = Field(default_factory=dict, description="页面设计配置")


class PageMetaUpdateIn(BaseModel):
    """更新页面请求"""
    name: Optional[str] = Field(None, description="页面名称")
    category: Optional[str] = Field(None, description="分类")
    description: Optional[str] = Field(None, description="描述")
    sort: Optional[int] = Field(None, description="排序")
    page_config: Optional[Dict[str, Any]] = Field(None, description="页面设计配置")


class PageMetaOut(BaseModel):
    """页面详情输出"""
    id: str
    name: str
    code: str
    category: str
    description: str
    status: str
    version: int
    page_config: Dict[str, Any]
    sort: int
    sys_create_datetime: str
    sys_update_datetime: str

    model_config = ConfigDict(from_attributes=True)


class PageMetaListOut(BaseModel):
    """页面列表输出"""
    id: str
    name: str
    code: str
    category: str
    description: str
    status: str
    version: int
    sort: int
    sys_create_datetime: str
    sys_update_datetime: str

    model_config = ConfigDict(from_attributes=True)


# ============ 导入导出 Schema ============

class PageExportOut(BaseModel):
    """页面配置导出"""
    name: str
    code: str
    category: str
    description: str
    page_config: Dict[str, Any]


class PageImportIn(BaseModel):
    """页面配置导入"""
    name: str = Field(..., description="页面名称")
    code: str = Field(..., description="页面编码")
    category: str = Field("", description="分类")
    description: str = Field("", description="描述")
    page_config: Dict[str, Any] = Field(default_factory=dict, description="页面设计配置")


# ============ 发布配置 Schema ============

class PagePublishIn(BaseModel):
    """发布页面请求（含菜单配置）"""
    menu_name: str = Field(..., description="菜单名称")
    menu_parent_id: Optional[str] = Field(None, description="上级菜单ID")
    menu_icon: str = Field("lucide:layout-dashboard", description="菜单图标")
    menu_order: int = Field(0, description="菜单排序")
