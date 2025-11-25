#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
登录日志模型 - Login Log Model
记录用户的所有登录操作，包括成功和失败的尝试
"""
from django.db import models
from common.fu_model import RootModel


class LoginLog(RootModel):
    """
    登录日志模型 - 完整记录用户登录信息
    
    特性：
    1. 记录用户标识（用户名和用户ID）
    2. 记录登录结果（成功/失败）
    3. 记录失败原因
    4. 记录登录IP地址
    5. 记录用户代理（浏览器信息）
    6. 记录登录时间戳
    7. 记录设备信息
    """
    
    # 登录结果选择
    STATUS_CHOICES = [
        (0, '失败'),  # 登录失败
        (1, '成功'),  # 登录成功
    ]
    
    # 失败原因选择
    FAILURE_REASON_CHOICES = [
        (0, '未知错误'),
        (1, '用户不存在'),
        (2, '密码错误'),
        (3, '用户已禁用'),
        (4, '用户已锁定'),
        (5, '用户不激活'),
        (6, '账户异常'),
        (7, '其他错误'),
    ]
    
    # 登录方式选择
    LOGIN_TYPE_CHOICES = [
        ('password', '密码登录'),
        ('code', '验证码登录'),
        ('qrcode', '二维码登录'),
        ('gitee', 'Gitee OAuth'),
        ('github', 'GitHub OAuth'),
        ('qq', 'QQ OAuth'),
        ('google', 'Google OAuth'),
        ('wechat', '微信 OAuth'),
        ('microsoft', '微软 OAuth'),
        ('dingtalk', '钉钉 OAuth'),
        ('feishu', '飞书 OAuth'),
    ]
    
    # 用户ID
    user_id = models.CharField(
        max_length=36,
        null=True,
        blank=True,
        help_text="用户ID",
        db_index=True,
    )
    
    # 用户名
    username = models.CharField(
        max_length=150,
        help_text="用户名",
        db_index=True,
    )
    
    # 登录方式
    login_type = models.CharField(
        max_length=20,
        choices=LOGIN_TYPE_CHOICES,
        default='password',
        help_text="登录方式",
        db_index=True,
    )
    
    # 登录状态：0-失败，1-成功
    status = models.IntegerField(
        choices=STATUS_CHOICES,
        default=0,
        help_text="登录状态",
        db_index=True,
    )
    
    # 失败原因（仅当status=0时有效）
    failure_reason = models.IntegerField(
        choices=FAILURE_REASON_CHOICES,
        null=True,
        blank=True,
        help_text="登录失败原因",
    )
    
    # 失败详细信息
    failure_message = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="登录失败详细信息",
    )
    
    # 登录IP地址
    login_ip = models.GenericIPAddressField(
        help_text="登录IP地址",
        db_index=True,
    )
    
    # IP属地（地区信息，可选）
    ip_location = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="IP属地（地区）",
    )
    
    # 用户代理（浏览器信息）
    user_agent = models.TextField(
        null=True,
        blank=True,
        help_text="用户代理字符串（浏览器信息）",
    )
    
    # 浏览器类型
    browser_type = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="浏览器类型",
    )
    
    # 操作系统
    os_type = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="操作系统类型",
    )
    
    # 设备类型（桌面、移动、平板等）
    device_type = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text="设备类型（desktop/mobile/tablet/other）",
    )
    
    # 登录时长（从登录到退出，单位：秒）
    duration = models.IntegerField(
        null=True,
        blank=True,
        default=0,
        help_text="登录会话时长（秒）",
    )
    
    # 会话ID
    session_id = models.CharField(
        max_length=128,
        null=True,
        blank=True,
        help_text="会话ID",
        unique=True,
    )
    
    # 备注
    remark = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="备注信息",
    )
    
    class Meta:
        db_table = "core_login_log"
        ordering = ("-sys_create_datetime",)
        verbose_name = "登录日志"
        verbose_name_plural = verbose_name
        indexes = [
            models.Index(fields=['user_id', 'sys_create_datetime']),
            models.Index(fields=['username', 'status']),
            models.Index(fields=['status', 'sys_create_datetime']),
            models.Index(fields=['login_ip', 'sys_create_datetime']),
            models.Index(fields=['login_type', 'sys_create_datetime']),
            models.Index(fields=['user_id', 'login_type']),
        ]
    
    def __str__(self):
        status_name = dict(self.STATUS_CHOICES).get(self.status, 'UNKNOWN')
        return f"{self.username} - {status_name} - {self.sys_create_datetime}"
    
    def get_status_display_name(self):
        """获取登录状态的显示名称"""
        status_map = dict(self.STATUS_CHOICES)
        return status_map.get(self.status, 'UNKNOWN')
    
    def get_failure_reason_display_name(self):
        """获取失败原因的显示名称"""
        if self.failure_reason is None:
            return None
        reason_map = dict(self.FAILURE_REASON_CHOICES)
        return reason_map.get(self.failure_reason, 'UNKNOWN')
    
    def is_success(self):
        """判断登录是否成功"""
        return self.status == 1
    
    def is_failed(self):
        """判断登录是否失败"""
        return self.status == 0
    
    def get_login_type_display_name(self):
        """获取登录方式的显示名称"""
        type_map = dict(self.LOGIN_TYPE_CHOICES)
        return type_map.get(self.login_type, '未知方式')

