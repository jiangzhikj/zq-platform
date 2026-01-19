#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author: 臧成龙
@Contact: 939589097@qq.com
@Time: 2025-12-31
@File: api.py
@Desc: 消息中心 API（异步版本）
"""
"""
消息中心 API（异步版本）
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.base_schema import PaginatedResponse, ResponseModel
from core.message.schema import (
    MessageOut,
    MessageListOut,
    UnreadCountOut,
    MarkReadInput,
    AnnouncementCreate,
    AnnouncementUpdate,
    AnnouncementOut,
    AnnouncementListOut,
    UserAnnouncementOut,
    ReadStatsOut,
)
from core.message.service import MessageService, AnnouncementService

router = APIRouter(prefix="/message", tags=["消息中心"])


# ============ 消息 API ============

@router.get("/list", response_model=PaginatedResponse[MessageListOut], summary="消息列表")
async def list_messages(
        request: Request,
        msg_type: str = Query(None, description="消息类型"),
        status: str = Query(None, description="状态: unread/read"),
        page: int = Query(default=1, ge=1, description="页码"),
        page_size: int = Query(default=20, ge=1, le=100, alias="pageSize", description="每页数量"),
        db: AsyncSession = Depends(get_db),
):
    """获取当前用户的消息列表"""
    user_id = request.state.user_id
    items, total = await MessageService.get_list(
        db=db,
        user_id=user_id,
        msg_type=msg_type,
        status=status,
        page=page,
        page_size=page_size,
    )

    return PaginatedResponse(
        items=[_build_message_list_out(item) for item in items],
        total=total,
    )


@router.get("/unread-count", response_model=UnreadCountOut, summary="未读数量")
async def get_unread_count(
        request: Request,
        db: AsyncSession = Depends(get_db),
):
    """获取未读消息数量"""
    user_id = request.state.user_id
    total = await MessageService.get_unread_count(db, user_id)
    by_type = await MessageService.get_unread_count_by_type(db, user_id)

    return UnreadCountOut(total=total, by_type=by_type)


@router.post("/read-all", response_model=ResponseModel, summary="全部已读")
async def mark_all_as_read(
        request: Request,
        data: Optional[MarkReadInput] = Body(None),
        db: AsyncSession = Depends(get_db),
):
    """标记所有消息为已读"""
    user_id = request.state.user_id
    msg_type = data.msg_type if data else None
    count = await MessageService.mark_all_as_read(db, user_id, msg_type)

    return ResponseModel(message=f"已标记 {count} 条消息为已读")


@router.delete("/clear-read", response_model=ResponseModel, summary="清空已读")
async def clear_read_messages(
        request: Request,
        db: AsyncSession = Depends(get_db),
):
    """清空所有已读消息"""
    user_id = request.state.user_id
    count = await MessageService.delete_all_read(db, user_id)

    return ResponseModel(message=f"已删除 {count} 条已读消息")


@router.get("/{message_id}", response_model=MessageOut, summary="消息详情")
async def get_message(
        request: Request,
        message_id: str,
        db: AsyncSession = Depends(get_db),
):
    """获取消息详情"""
    user_id = request.state.user_id
    message = await MessageService.get_by_id(db, message_id, user_id)
    if not message:
        raise HTTPException(status_code=404, detail="消息不存在")

    return _build_message_out(message)


@router.post("/{message_id}/read", response_model=ResponseModel, summary="标记已读")
async def mark_as_read(
        request: Request,
        message_id: str,
        db: AsyncSession = Depends(get_db),
):
    """标记单条消息为已读"""
    user_id = request.state.user_id
    success = await MessageService.mark_as_read(db, message_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="消息不存在")

    return ResponseModel(message="已标记为已读")


@router.delete("/{message_id}", response_model=ResponseModel, summary="删除消息")
async def delete_message(
        request: Request,
        message_id: str,
        db: AsyncSession = Depends(get_db),
):
    """删除单条消息"""
    user_id = request.state.user_id
    success = await MessageService.delete(db, message_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="消息不存在")

    return ResponseModel(message="删除成功")


# ============ 公告管理端 API ============

announcement_router = APIRouter(prefix="/announcement", tags=["公告管理"])


@announcement_router.get("/admin/list", response_model=PaginatedResponse[AnnouncementListOut], summary="公告列表（管理）")
async def list_announcements(
        status: str = Query(None, description="状态: draft/published/expired"),
        keyword: str = Query(None, description="关键词搜索"),
        page: int = Query(default=1, ge=1, description="页码"),
        page_size: int = Query(default=20, ge=1, le=100, alias="pageSize", description="每页数量"),
        db: AsyncSession = Depends(get_db),
):
    """获取公告列表（管理端）"""
    items, total = await AnnouncementService.get_list(
        db=db,
        page=page,
        page_size=page_size,
        status=status,
        keyword=keyword,
    )

    return PaginatedResponse(
        items=[_build_announcement_list_out(item) for item in items],
        total=total,
    )


@announcement_router.get("/admin/{announcement_id}", response_model=AnnouncementOut, summary="公告详情（管理）")
async def get_announcement(
        announcement_id: str,
        db: AsyncSession = Depends(get_db),
):
    """获取公告详情"""
    announcement = await AnnouncementService.get_by_id(db, announcement_id)
    if not announcement:
        raise HTTPException(status_code=404, detail="公告不存在")

    return await _build_announcement_out(db, announcement)


@announcement_router.post("/admin", response_model=AnnouncementOut, summary="创建公告")
async def create_announcement(
        request: Request,
        data: AnnouncementCreate,
        db: AsyncSession = Depends(get_db),
):
    """创建公告"""
    user_id = request.state.user_id
    announcement = await AnnouncementService.create(db, data.model_dump(), user_id)
    return await _build_announcement_out(db, announcement)


@announcement_router.put("/admin/{announcement_id}", response_model=AnnouncementOut, summary="更新公告")
async def update_announcement(
        request: Request,
        announcement_id: str,
        data: AnnouncementUpdate,
        db: AsyncSession = Depends(get_db),
):
    """更新公告"""
    user_id = request.state.user_id
    announcement = await AnnouncementService.update(
        db, announcement_id, data.model_dump(exclude_unset=True), user_id
    )
    if not announcement:
        raise HTTPException(status_code=404, detail="公告不存在")

    return await _build_announcement_out(db, announcement)


@announcement_router.delete("/admin/{announcement_id}", response_model=ResponseModel, summary="删除公告")
async def delete_announcement(
        request: Request,
        announcement_id: str,
        db: AsyncSession = Depends(get_db),
):
    """删除公告"""
    user_id = request.state.user_id
    success = await AnnouncementService.delete(db, announcement_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="公告不存在")

    return ResponseModel(message="删除成功")


@announcement_router.post("/admin/{announcement_id}/publish", response_model=AnnouncementOut, summary="发布公告")
async def publish_announcement(
        request: Request,
        announcement_id: str,
        db: AsyncSession = Depends(get_db),
):
    """发布公告"""
    user_id = request.state.user_id
    try:
        announcement = await AnnouncementService.publish(db, announcement_id, user_id)
        if not announcement:
            raise HTTPException(status_code=404, detail="公告不存在")
        return await _build_announcement_out(db, announcement)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@announcement_router.get("/admin/{announcement_id}/stats", response_model=ReadStatsOut, summary="阅读统计")
async def get_read_stats(
        announcement_id: str,
        db: AsyncSession = Depends(get_db),
):
    """获取公告阅读统计"""
    stats = await AnnouncementService.get_read_stats(db, announcement_id)
    if not stats:
        raise HTTPException(status_code=404, detail="公告不存在")

    return ReadStatsOut(**stats)


# ============ 公告用户端 API ============

@announcement_router.get("/user/list", response_model=PaginatedResponse[UserAnnouncementOut], summary="我的公告")
async def list_user_announcements(
        request: Request,
        unread_only: bool = Query(False, description="只看未读"),
        page: int = Query(default=1, ge=1, description="页码"),
        page_size: int = Query(default=20, ge=1, le=100, alias="pageSize", description="每页数量"),
        db: AsyncSession = Depends(get_db),
):
    """获取当前用户可见的公告列表"""
    user_id = request.state.user_id
    # 从token中获取用户的部门和角色信息
    user_dept_ids = []
    user_role_ids = []
    if hasattr(request.state, 'token_payload'):
        payload = request.state.token_payload
        if payload.get('dept_id'):
            user_dept_ids = [payload.get('dept_id')]
        if payload.get('role_id'):
            user_role_ids = [payload.get('role_id')]

    items, total = await AnnouncementService.get_user_announcements(
        db=db,
        user_id=user_id,
        user_dept_ids=user_dept_ids,
        user_role_ids=user_role_ids,
        page=page,
        page_size=page_size,
        unread_only=unread_only,
    )

    return PaginatedResponse(
        items=[await _build_user_announcement_out(db, item) for item in items],
        total=total,
    )


@announcement_router.get("/user/unread-count", response_model=dict, summary="未读公告数量")
async def get_user_unread_count(
        request: Request,
        db: AsyncSession = Depends(get_db),
):
    """获取未读公告数量"""
    user_id = request.state.user_id
    user_dept_ids = []
    user_role_ids = []
    if hasattr(request.state, 'token_payload'):
        payload = request.state.token_payload
        if payload.get('dept_id'):
            user_dept_ids = [payload.get('dept_id')]
        if payload.get('role_id'):
            user_role_ids = [payload.get('role_id')]

    count = await AnnouncementService.get_unread_count(
        db, user_id, user_dept_ids, user_role_ids
    )
    return {"count": count}


@announcement_router.get("/user/{announcement_id}", response_model=UserAnnouncementOut, summary="公告详情")
async def get_user_announcement(
        request: Request,
        announcement_id: str,
        db: AsyncSession = Depends(get_db),
):
    """获取公告详情并标记已读"""
    user_id = request.state.user_id
    announcement = await AnnouncementService.get_by_id(db, announcement_id)
    if not announcement:
        raise HTTPException(status_code=404, detail="公告不存在")

    # 标记已读
    await AnnouncementService.mark_as_read(db, announcement_id, user_id)

    # 重新获取以更新is_read状态
    announcement.is_read = True

    return await _build_user_announcement_out(db, announcement)


@announcement_router.post("/user/{announcement_id}/read", response_model=ResponseModel, summary="标记已读")
async def mark_announcement_as_read(
        request: Request,
        announcement_id: str,
        db: AsyncSession = Depends(get_db),
):
    """标记公告为已读"""
    user_id = request.state.user_id
    success = await AnnouncementService.mark_as_read(db, announcement_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="公告不存在")

    return ResponseModel(message="已标记为已读")


# ============ 辅助函数 ============

def _build_message_out(message) -> dict:
    """构建消息详情输出"""
    return {
        "id": str(message.id),
        "title": message.title,
        "content": message.content,
        "msg_type": message.msg_type,
        "status": message.status,
        "link_type": message.link_type or "",
        "link_id": message.link_id or "",
        "sender_name": "",  # 需要关联查询
        "read_at": message.read_at,
        "created_at": message.sys_create_datetime,
    }


def _build_message_list_out(message) -> dict:
    """构建消息列表输出"""
    return {
        "id": str(message.id),
        "title": message.title,
        "content": message.content[:100] if message.content else "",
        "msg_type": message.msg_type,
        "status": message.status,
        "link_type": message.link_type or "",
        "link_id": message.link_id or "",
        "created_at": message.sys_create_datetime,
    }


async def _build_announcement_out(db: AsyncSession, announcement) -> dict:
    """构建公告输出"""
    publisher_name = ""
    if announcement.publisher_id:
        from core.user.model import User
        from sqlalchemy import select
        stmt = select(User).where(User.id == announcement.publisher_id)
        result = await db.execute(stmt)
        publisher = result.scalar_one_or_none()
        if publisher:
            publisher_name = publisher.name or ""

    return {
        "id": str(announcement.id),
        "title": announcement.title,
        "content": announcement.content,
        "summary": announcement.summary or "",
        "status": announcement.status,
        "priority": announcement.priority,
        "is_top": announcement.is_top,
        "target_type": announcement.target_type,
        "target_ids": announcement.target_ids or [],
        "publish_time": announcement.publish_time,
        "expire_time": announcement.expire_time,
        "publisher_id": str(announcement.publisher_id) if announcement.publisher_id else None,
        "publisher_name": publisher_name,
        "read_count": announcement.read_count or 0,
        "created_at": announcement.sys_create_datetime,
    }


def _build_announcement_list_out(announcement) -> dict:
    """构建公告列表输出"""
    return {
        "id": str(announcement.id),
        "title": announcement.title,
        "summary": announcement.summary or "",
        "status": announcement.status,
        "priority": announcement.priority,
        "is_top": announcement.is_top,
        "target_type": announcement.target_type,
        "publisher_name": "",  # 需要关联查询
        "read_count": announcement.read_count or 0,
        "publish_time": announcement.publish_time,
        "created_at": announcement.sys_create_datetime,
    }


async def _build_user_announcement_out(db: AsyncSession, announcement) -> dict:
    """构建用户公告输出"""
    publisher_name = ""
    if announcement.publisher_id:
        from core.user.model import User
        from sqlalchemy import select
        stmt = select(User).where(User.id == announcement.publisher_id)
        result = await db.execute(stmt)
        publisher = result.scalar_one_or_none()
        if publisher:
            publisher_name = publisher.name or ""

    return {
        "id": str(announcement.id),
        "title": announcement.title,
        "summary": announcement.summary or "",
        "content": announcement.content,
        "priority": announcement.priority,
        "is_top": announcement.is_top,
        "is_read": getattr(announcement, "is_read", False),
        "publisher_name": publisher_name,
        "publish_time": announcement.publish_time,
    }
