#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author: 臧成龙
@Contact: 939589097@qq.com
@Time: 2025-12-31
@File: service.py
@Desc: 消息中心服务（异步版本）
"""
"""
消息中心服务（异步版本）
"""
import logging
import re
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

from sqlalchemy import select, update, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from core.message.model import Message, Announcement, AnnouncementRead

logger = logging.getLogger(__name__)


class MessageService:
    """消息管理服务"""

    @staticmethod
    async def get_list(
            db: AsyncSession,
            user_id: str,
            msg_type: str = None,
            status: str = None,
            page: int = 1,
            page_size: int = 20,
    ) -> Tuple[List[Message], int]:
        """获取用户消息列表"""
        conditions = [
            Message.recipient_id == user_id,
            Message.is_deleted == False,
        ]

        if msg_type:
            conditions.append(Message.msg_type == msg_type)
        if status:
            conditions.append(Message.status == status)

        # 获取总数
        count_stmt = select(func.count(Message.id)).where(and_(*conditions))
        total_result = await db.execute(count_stmt)
        total = total_result.scalar() or 0

        # 获取列表
        offset = (page - 1) * page_size
        stmt = select(Message).where(and_(*conditions)).order_by(
            Message.sys_create_datetime.desc()
        ).offset(offset).limit(page_size)

        result = await db.execute(stmt)
        items = list(result.scalars().all())

        return items, total

    @staticmethod
    async def get_unread_count(db: AsyncSession, user_id: str) -> int:
        """获取未读消息数量"""
        stmt = select(func.count(Message.id)).where(
            Message.recipient_id == user_id,
            Message.status == "unread",
            Message.is_deleted == False,
        )
        result = await db.execute(stmt)
        return result.scalar() or 0

    @staticmethod
    async def get_unread_count_by_type(db: AsyncSession, user_id: str) -> Dict[str, int]:
        """按类型获取未读消息数量"""
        stmt = select(Message.msg_type, func.count(Message.id)).where(
            Message.recipient_id == user_id,
            Message.status == "unread",
            Message.is_deleted == False,
        ).group_by(Message.msg_type)

        result = await db.execute(stmt)
        return {row[0]: row[1] for row in result.all()}

    @staticmethod
    async def get_by_id(db: AsyncSession, message_id: str, user_id: str) -> Optional[Message]:
        """获取消息详情"""
        stmt = select(Message).where(
            Message.id == message_id,
            Message.recipient_id == user_id,
            Message.is_deleted == False,
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def mark_as_read(db: AsyncSession, message_id: str, user_id: str) -> bool:
        """标记消息为已读"""
        message = await MessageService.get_by_id(db, message_id, user_id)
        if not message:
            return False

        if message.status == "unread":
            message.status = "read"
            message.read_at = datetime.now()
            await db.commit()

        return True

    @staticmethod
    async def mark_all_as_read(db: AsyncSession, user_id: str, msg_type: str | None = None) -> int:
        """标记所有消息为已读"""
        conditions = [
            Message.recipient_id == user_id,
            Message.status == "unread",
            Message.is_deleted == False,
        ]

        if msg_type:
            conditions.append(Message.msg_type == msg_type)

        stmt = update(Message).where(and_(*conditions)).values(
            status="read",
            read_at=datetime.now(),
        )

        result = await db.execute(stmt)
        await db.commit()

        return result.rowcount

    @staticmethod
    async def delete(db: AsyncSession, message_id: str, user_id: str) -> bool:
        """删除消息（软删除）"""
        message = await MessageService.get_by_id(db, message_id, user_id)
        if not message:
            return False

        message.is_deleted = True
        await db.commit()

        return True

    @staticmethod
    async def delete_all_read(db: AsyncSession, user_id: str) -> int:
        """删除所有已读消息"""
        stmt = update(Message).where(
            Message.recipient_id == user_id,
            Message.status == "read",
            Message.is_deleted == False,
        ).values(is_deleted=True)

        result = await db.execute(stmt)
        await db.commit()

        return result.rowcount

    @staticmethod
    async def create_message(
            db: AsyncSession,
            recipient_id: str,
            title: str,
            content: str,
            msg_type: str = "system",
            link_type: str = "",
            link_id: str = "",
            sender_id: str = None,
    ) -> Message:
        """创建消息"""
        message = Message(
            recipient_id=recipient_id,
            title=title,
            content=content,
            msg_type=msg_type,
            link_type=link_type,
            link_id=link_id,
            sender_id=sender_id,
        )
        db.add(message)
        await db.commit()
        await db.refresh(message)
        return message

    @staticmethod
    async def batch_create_messages(
            db: AsyncSession,
            recipient_ids: List[str],
            title: str,
            content: str,
            msg_type: str = "system",
            link_type: str = "",
            link_id: str = "",
            sender_id: str = None,
    ) -> List[Message]:
        """批量创建消息"""
        messages = []
        for recipient_id in recipient_ids:
            message = Message(
                recipient_id=recipient_id,
                title=title,
                content=content,
                msg_type=msg_type,
                link_type=link_type,
                link_id=link_id,
                sender_id=sender_id,
            )
            messages.append(message)
            db.add(message)

        await db.commit()
        return messages


class AnnouncementService:
    """公告管理服务"""

    @staticmethod
    async def get_list(
            db: AsyncSession,
            page: int = 1,
            page_size: int = 20,
            status: str = None,
            keyword: str = None,
    ) -> Tuple[List[Announcement], int]:
        """获取公告列表（管理端）"""
        conditions = [Announcement.is_deleted == False]

        if status:
            conditions.append(Announcement.status == status)
        if keyword:
            conditions.append(
                or_(
                    Announcement.title.ilike(f"%{keyword}%"),
                    Announcement.content.ilike(f"%{keyword}%"),
                )
            )

        # 获取总数
        count_stmt = select(func.count(Announcement.id)).where(and_(*conditions))
        total_result = await db.execute(count_stmt)
        total = total_result.scalar() or 0

        # 获取列表
        offset = (page - 1) * page_size
        stmt = select(Announcement).where(and_(*conditions)).order_by(
            Announcement.is_top.desc(),
            Announcement.priority.desc(),
            Announcement.publish_time.desc(),
        ).offset(offset).limit(page_size)

        result = await db.execute(stmt)
        items = list(result.scalars().all())

        return items, total

    @staticmethod
    async def get_user_announcements(
            db: AsyncSession,
            user_id: str,
            user_dept_ids: List[str] = None,
            user_role_ids: List[str] = None,
            page: int = 1,
            page_size: int = 20,
            unread_only: bool = False,
    ) -> Tuple[List[Announcement], int]:
        """获取用户可见的公告列表"""
        now = datetime.now()

        # 基础查询：已发布且未过期
        conditions = [
            Announcement.status == "published",
            Announcement.is_deleted == False,
            or_(Announcement.expire_time.is_(None), Announcement.expire_time > now),
        ]

        # 过滤接收范围 - 使用JSONB的contains操作符
        target_conditions = [Announcement.target_type == "all"]

        if user_dept_ids:
            for dept_id in user_dept_ids:
                target_conditions.append(
                    and_(
                        Announcement.target_type == "dept",
                        Announcement.target_ids.op('@>')([dept_id])
                    )
                )

        if user_role_ids:
            for role_id in user_role_ids:
                target_conditions.append(
                    and_(
                        Announcement.target_type == "role",
                        Announcement.target_ids.op('@>')([role_id])
                    )
                )

        target_conditions.append(
            and_(
                Announcement.target_type == "user",
                Announcement.target_ids.op('@>')([user_id])
            )
        )

        conditions.append(or_(*target_conditions))

        # 只看未读
        if unread_only:
            read_stmt = select(AnnouncementRead.announcement_id).where(
                AnnouncementRead.user_id == user_id
            )
            read_result = await db.execute(read_stmt)
            read_ids = [row[0] for row in read_result.all()]
            if read_ids:
                conditions.append(Announcement.id.notin_(read_ids))

        # 获取总数
        count_stmt = select(func.count(Announcement.id)).where(and_(*conditions))
        total_result = await db.execute(count_stmt)
        total = total_result.scalar() or 0

        # 获取列表
        offset = (page - 1) * page_size
        stmt = select(Announcement).where(and_(*conditions)).order_by(
            Announcement.is_top.desc(),
            Announcement.priority.desc(),
            Announcement.publish_time.desc(),
        ).offset(offset).limit(page_size)

        result = await db.execute(stmt)
        items = list(result.scalars().all())

        # 标记已读状态
        if items:
            read_stmt = select(AnnouncementRead.announcement_id).where(
                AnnouncementRead.user_id == user_id,
                AnnouncementRead.announcement_id.in_([a.id for a in items])
            )
            read_result = await db.execute(read_stmt)
            read_ids = set(row[0] for row in read_result.all())

            for item in items:
                item.is_read = item.id in read_ids

        return items, total

    @staticmethod
    async def get_by_id(db: AsyncSession, announcement_id: str) -> Optional[Announcement]:
        """获取公告详情"""
        stmt = select(Announcement).where(
            Announcement.id == announcement_id,
            Announcement.is_deleted == False,
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def create(
            db: AsyncSession,
            data: Dict[str, Any],
            user_id: str,
    ) -> Announcement:
        """创建公告"""
        announcement = Announcement(
            title=data["title"],
            content=data["content"],
            summary=data.get("summary", ""),
            status=data.get("status", "draft"),
            priority=data.get("priority", 0),
            is_top=data.get("is_top", False),
            target_type=data.get("target_type", "all"),
            target_ids=data.get("target_ids", []),
            publish_time=data.get("publish_time"),
            expire_time=data.get("expire_time"),
            publisher_id=user_id,
            sys_creator_id=user_id,
            sys_modifier_id=user_id,
        )
        db.add(announcement)
        await db.commit()
        await db.refresh(announcement)

        return announcement

    @staticmethod
    async def update(
            db: AsyncSession,
            announcement_id: str,
            data: Dict[str, Any],
            user_id: str,
    ) -> Optional[Announcement]:
        """更新公告"""
        announcement = await AnnouncementService.get_by_id(db, announcement_id)
        if not announcement:
            return None

        # 更新字段
        for field in ["title", "content", "summary", "status", "priority",
                      "is_top", "target_type", "target_ids", "publish_time", "expire_time"]:
            if field in data and data[field] is not None:
                setattr(announcement, field, data[field])

        announcement.sys_modifier_id = user_id
        await db.commit()
        await db.refresh(announcement)

        return announcement

    @staticmethod
    async def delete(db: AsyncSession, announcement_id: str, user_id: str) -> bool:
        """删除公告（软删除）"""
        announcement = await AnnouncementService.get_by_id(db, announcement_id)
        if not announcement:
            return False

        announcement.is_deleted = True
        announcement.sys_modifier_id = user_id
        await db.commit()

        return True

    @staticmethod
    async def publish(
            db: AsyncSession,
            announcement_id: str,
            user_id: str,
    ) -> Optional[Announcement]:
        """发布公告"""
        announcement = await AnnouncementService.get_by_id(db, announcement_id)
        if not announcement:
            return None

        if announcement.status != "draft":
            raise ValueError("只能发布草稿状态的公告")

        announcement.status = "published"
        announcement.publish_time = datetime.now()
        announcement.publisher_id = user_id
        announcement.sys_modifier_id = user_id
        await db.commit()
        await db.refresh(announcement)

        return announcement

    @staticmethod
    async def mark_as_read(
            db: AsyncSession,
            announcement_id: str,
            user_id: str,
    ) -> bool:
        """标记公告为已读"""
        announcement = await AnnouncementService.get_by_id(db, announcement_id)
        if not announcement:
            return False

        # 检查是否已读
        stmt = select(AnnouncementRead).where(
            AnnouncementRead.announcement_id == announcement_id,
            AnnouncementRead.user_id == user_id,
        )
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()

        if not existing:
            # 创建阅读记录
            read_record = AnnouncementRead(
                announcement_id=announcement_id,
                user_id=user_id,
                read_at=datetime.now(),
                sys_creator_id=user_id,
                sys_modifier_id=user_id,
            )
            db.add(read_record)

            # 更新阅读计数
            announcement.read_count = (announcement.read_count or 0) + 1

            await db.commit()

        return True

    @staticmethod
    async def get_unread_count(
            db: AsyncSession,
            user_id: str,
            user_dept_ids: List[str] = None,
            user_role_ids: List[str] = None,
    ) -> int:
        """获取未读公告数量"""
        now = datetime.now()

        # 基础查询
        conditions = [
            Announcement.status == "published",
            Announcement.is_deleted == False,
            or_(Announcement.expire_time.is_(None), Announcement.expire_time > now),
        ]

        # 过滤接收范围 - 使用JSONB的contains操作符
        target_conditions = [Announcement.target_type == "all"]

        if user_dept_ids:
            for dept_id in user_dept_ids:
                target_conditions.append(
                    and_(
                        Announcement.target_type == "dept",
                        Announcement.target_ids.op('@>')([dept_id])
                    )
                )

        if user_role_ids:
            for role_id in user_role_ids:
                target_conditions.append(
                    and_(
                        Announcement.target_type == "role",
                        Announcement.target_ids.op('@>')([role_id])
                    )
                )

        target_conditions.append(
            and_(
                Announcement.target_type == "user",
                Announcement.target_ids.op('@>')([user_id])
            )
        )

        conditions.append(or_(*target_conditions))

        # 排除已读
        read_stmt = select(AnnouncementRead.announcement_id).where(
            AnnouncementRead.user_id == user_id
        )
        read_result = await db.execute(read_stmt)
        read_ids = [row[0] for row in read_result.all()]
        if read_ids:
            conditions.append(Announcement.id.notin_(read_ids))

        # 获取数量
        count_stmt = select(func.count(Announcement.id)).where(and_(*conditions))
        result = await db.execute(count_stmt)
        return result.scalar() or 0

    @staticmethod
    async def get_read_stats(db: AsyncSession, announcement_id: str) -> Optional[Dict[str, Any]]:
        """获取公告阅读统计"""
        announcement = await AnnouncementService.get_by_id(db, announcement_id)
        if not announcement:
            return None

        # 获取阅读记录
        stmt = select(AnnouncementRead).where(
            AnnouncementRead.announcement_id == announcement_id
        ).order_by(AnnouncementRead.read_at.desc()).limit(100)

        result = await db.execute(stmt)
        reads = result.scalars().all()

        # 获取用户信息
        from core.user.model import User
        user_ids = [r.user_id for r in reads]
        if user_ids:
            user_stmt = select(User).where(User.id.in_(user_ids))
            user_result = await db.execute(user_stmt)
            users = {u.id: u for u in user_result.scalars().all()}
        else:
            users = {}

        return {
            "total_read": len(reads),
            "readers": [
                {
                    "user_id": r.user_id,
                    "user_name": users.get(r.user_id).name if users.get(r.user_id) else "",
                    "read_at": r.read_at.isoformat() if r.read_at else None,
                }
                for r in reads
            ]
        }


class NotifyService:
    """通知服务"""

    @staticmethod
    def parse_template(template: str, context: Dict[str, Any]) -> str:
        """解析模板变量"""
        if not template or not context:
            return template

        def replace_var(match):
            var_path = match.group(1)
            parts = var_path.split(".")
            value = context

            for part in parts:
                if isinstance(value, dict):
                    value = value.get(part, "")
                else:
                    value = ""
                    break

            return str(value) if value else ""

        return re.sub(r"\$\{([^}]+)\}", replace_var, template)

    @staticmethod
    async def send(
            db: AsyncSession,
            recipient_ids: List[str],
            title: str,
            content: str,
            channels: List[str] = None,
            msg_type: str = "system",
            context: Dict[str, Any] = None,
            link_type: str = "",
            link_id: str = "",
            sender_id: str = None,
    ) -> Dict[str, bool]:
        """发送通知"""
        if channels is None:
            channels = ["site"]

        # 解析模板变量
        if context:
            title = NotifyService.parse_template(title, context)
            content = NotifyService.parse_template(content, context)

        results = {}

        for channel in channels:
            try:
                if channel == "site":
                    await MessageService.batch_create_messages(
                        db=db,
                        recipient_ids=recipient_ids,
                        title=title,
                        content=content,
                        msg_type=msg_type,
                        link_type=link_type,
                        link_id=link_id,
                        sender_id=sender_id,
                    )
                    results["site"] = True
                    logger.info(f"站内消息发送成功: {len(recipient_ids)} 条")
                else:
                    logger.warning(f"未实现的通知渠道: {channel}")
                    results[channel] = False
            except Exception as e:
                logger.error(f"发送通知失败 [{channel}]: {e}")
                results[channel] = False

        return results
