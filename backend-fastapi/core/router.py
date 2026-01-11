#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Core模块统一路由入口
"""
from fastapi import APIRouter

from core.auth.api import router as auth_router
from core.dept.api import router as dept_router
from core.dict.api import router as dict_router
from core.dict_item.api import router as dict_item_router
from core.menu.api import router as menu_router
from core.permission.api import router as permission_router
from core.post.api import router as post_router
from core.role.api import router as role_router
from core.user.api import router as user_router
from core.file_manager.router import router as file_manager_router
from core.redis_monitor.api import router as redis_monitor_router
from core.server_monitor.api import router as server_monitor_router
from core.database_monitor.api import router as database_monitor_router
from core.redis_manager.api import router as redis_manager_router
from core.database_manager.api import router as database_manager_router
from core.message.api import router as message_router
from core.message.api import announcement_router
from core.page_manager.api import router as page_manager_router
from core.login_log.api import router as login_log_router
from core.data_source.api import router as data_source_router
from core.oauth.api import router as oauth_router

router = APIRouter()

# 注册子模块路由
router.include_router(auth_router)
router.include_router(dept_router)
router.include_router(dict_router)
router.include_router(dict_item_router)
router.include_router(menu_router)
router.include_router(permission_router)
router.include_router(post_router)
router.include_router(role_router)
router.include_router(user_router)
router.include_router(file_manager_router)
router.include_router(redis_monitor_router)
router.include_router(server_monitor_router)
router.include_router(database_monitor_router)
router.include_router(redis_manager_router)
router.include_router(database_manager_router)
router.include_router(message_router)
router.include_router(announcement_router)
router.include_router(page_manager_router)
router.include_router(login_log_router)
router.include_router(data_source_router)
router.include_router(oauth_router)
