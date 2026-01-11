#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
页面管理 API（异步版本）
页面元数据的 CRUD、发布、复制、导入导出
"""
import json
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.base_schema import PaginatedResponse
from core.page_manager.schema import (
    PageImportIn,
    PageMetaCreateIn,
    PageMetaListOut,
    PageMetaOut,
    PageMetaUpdateIn,
    PagePublishIn,
)
from core.page_manager.service import PageService, PageServiceException

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/page", tags=["页面管理"])


# ============ 辅助函数 ============

def _format_datetime(dt) -> str:
    """格式化日期时间"""
    if dt:
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    return ""


def _build_page_out(page) -> dict:
    """构建页面详情输出"""
    return {
        "id": str(page.id),
        "name": page.name,
        "code": page.code,
        "category": page.category or "",
        "description": page.description or "",
        "status": page.status,
        "version": page.version,
        "page_config": page.page_config or {},
        "sort": page.sort or 0,
        "sys_create_datetime": _format_datetime(page.sys_create_datetime),
        "sys_update_datetime": _format_datetime(page.sys_update_datetime),
    }


def _build_page_list_out(page) -> dict:
    """构建页面列表输出"""
    return {
        "id": str(page.id),
        "name": page.name,
        "code": page.code,
        "category": page.category or "",
        "description": page.description or "",
        "status": page.status,
        "version": page.version,
        "sort": page.sort or 0,
        "sys_create_datetime": _format_datetime(page.sys_create_datetime),
        "sys_update_datetime": _format_datetime(page.sys_update_datetime),
    }


# ============ 页面元数据 CRUD ============

@router.get("/list", response_model=PaginatedResponse[PageMetaListOut], summary="页面列表")
async def list_pages(
        name: str = Query(None, description="页面名称"),
        code: str = Query(None, description="页面编码"),
        category: str = Query(None, description="分类"),
        status: str = Query(None, description="状态"),
        page: int = Query(default=1, ge=1, description="页码"),
        page_size: int = Query(default=20, ge=1, le=100, alias="pageSize", description="每页数量"),
        db: AsyncSession = Depends(get_db),
):
    """分页查询页面列表"""
    result = await PageService.list(
        db=db,
        page=page,
        page_size=page_size,
        name=name,
        code=code,
        category=category,
        status=status
    )

    return PaginatedResponse(
        items=[_build_page_list_out(item) for item in result["items"]],
        total=result["total"],
    )


@router.get("/categories", response_model=List[str], summary="获取分类列表")
async def get_categories(db: AsyncSession = Depends(get_db)):
    """获取所有页面分类"""
    return await PageService.get_categories(db)


@router.get("/code/{code}", response_model=PageMetaOut, summary="根据编码获取页面")
async def get_page_by_code(
        code: str,
        db: AsyncSession = Depends(get_db),
):
    """根据编码获取页面详情"""
    try:
        page = await PageService.get_by_code(db, code)
        return _build_page_out(page)
    except PageServiceException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{page_id}", response_model=PageMetaOut, summary="页面详情")
async def get_page(
        page_id: str,
        db: AsyncSession = Depends(get_db),
):
    """获取页面详情"""
    try:
        page = await PageService.get(db, page_id)
        return _build_page_out(page)
    except PageServiceException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("", response_model=PageMetaOut, summary="创建页面")
async def create_page(
        request: Request,
        data: PageMetaCreateIn,
        db: AsyncSession = Depends(get_db),
):
    """创建页面"""
    user_id = request.state.user_id

    try:
        page = await PageService.create(db, data.model_dump(), user_id)
        return _build_page_out(page)
    except PageServiceException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{page_id}", response_model=PageMetaOut, summary="更新页面")
async def update_page(
        request: Request,
        page_id: str,
        data: PageMetaUpdateIn,
        db: AsyncSession = Depends(get_db),
):
    """更新页面"""
    user_id = request.state.user_id

    try:
        page = await PageService.update(db, page_id, data.model_dump(exclude_none=True), user_id)
        return _build_page_out(page)
    except PageServiceException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/batch", summary="批量删除页面")
async def batch_delete_pages(
        ids: List[str] = Query(..., description="页面ID列表"),
        db: AsyncSession = Depends(get_db),
):
    """批量删除页面"""
    count = await PageService.batch_delete(db, ids)
    return {"count": count}


@router.delete("/{page_id}", response_model=PageMetaOut, summary="删除页面")
async def delete_page(
        page_id: str,
        db: AsyncSession = Depends(get_db),
):
    """删除页面"""
    try:
        page = await PageService.get(db, page_id)
        page_out = _build_page_out(page)
        await PageService.delete(db, page_id)
        return page_out
    except PageServiceException as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============ 发布/取消发布 ============

@router.post("/{page_id}/publish", response_model=PageMetaOut, summary="发布页面")
async def publish_page(
        page_id: str,
        data: PagePublishIn,
        db: AsyncSession = Depends(get_db),
):
    """发布页面并创建菜单"""
    try:
        page = await PageService.publish(db, page_id, data.model_dump())
        return _build_page_out(page)
    except PageServiceException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{page_id}/unpublish", response_model=PageMetaOut, summary="取消发布")
async def unpublish_page(
        page_id: str,
        db: AsyncSession = Depends(get_db),
):
    """取消发布页面并删除菜单"""
    try:
        page = await PageService.unpublish(db, page_id)
        return _build_page_out(page)
    except PageServiceException as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============ 复制 ============

@router.post("/{page_id}/copy", response_model=PageMetaOut, summary="复制页面")
async def copy_page(
        request: Request,
        page_id: str,
        new_code: str = Query(..., alias="newCode", description="新页面编码"),
        new_name: str = Query(None, alias="newName", description="新页面名称"),
        db: AsyncSession = Depends(get_db),
):
    """复制页面"""
    user_id = request.state.user_id

    try:
        page = await PageService.copy(db, page_id, new_code, new_name, user_id)
        return _build_page_out(page)
    except PageServiceException as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============ 导入/导出配置 ============

@router.get("/{page_id}/export", summary="导出页面配置")
async def export_page_config(
        page_id: str,
        db: AsyncSession = Depends(get_db),
):
    """导出页面配置为 JSON"""
    try:
        config = await PageService.export_config(db, page_id)

        # 返回 JSON 文件
        content = json.dumps(config, ensure_ascii=False, indent=2)

        return StreamingResponse(
            iter([content]),
            media_type="application/json",
            headers={
                "Content-Disposition": f'attachment; filename="{config["code"]}.json"'
            }
        )
    except PageServiceException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/import", response_model=PageMetaOut, summary="导入页面配置")
async def import_page_config(
        request: Request,
        data: PageImportIn,
        db: AsyncSession = Depends(get_db),
):
    """导入页面配置"""
    user_id = request.state.user_id

    try:
        page = await PageService.import_config(db, data.model_dump(), user_id)
        return _build_page_out(page)
    except PageServiceException as e:
        raise HTTPException(status_code=400, detail=str(e))
