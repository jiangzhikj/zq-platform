#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
User Model - 用户模型
用于管理系统用户
"""
from django.db import models
from django.core.validators import EmailValidator, RegexValidator
from django.contrib.auth.hashers import make_password, check_password
from common.fu_model import RootModel


class User(RootModel):
    """
    用户模型 - 系统用户管理
    
    改进点：
    1. 添加更详细的字段注释
    2. 添加用户状态字段
    3. 添加最后登录IP字段
    4. 添加用户类型字段
    5. 添加字段验证
    6. 优化索引
    7. 添加更多用户信息字段
    """
    
    # 用户类型选择
    USER_TYPE_CHOICES = [
        (0, '系统用户'),  # 系统内置用户，如admin
        (1, '普通用户'),  # 普通用户
        (2, '外部用户'),  # 外部用户（如供应商、客户）
    ]
    
    # 性别选择
    GENDER_CHOICES = [
        (0, '未知'),
        (1, '男'),
        (2, '女'),
    ]
    
    # 用户状态选择
    STATUS_CHOICES = [
        (0, '禁用'),
        (1, '正常'),
        (2, '锁定'),
    ]
    
    # 用户名
    username = models.CharField(
        max_length=150,
        unique=True,
        db_index=True,
        help_text="用户名",
        error_messages={
            'unique': "该用户名已存在。",
        },
    )
    
    # 密码
    password = models.CharField(
        max_length=128,
        help_text="密码（加密存储）",
    )
    
    # 是否为超级管理员
    is_superuser = models.BooleanField(
        default=False,
        help_text="超级管理员标识",
        db_index=True,
    )
    
    # 最后登录时间
    last_login = models.DateTimeField(
        null=True,
        blank=True,
        help_text="最后登录时间",
    )
    
    # 邮箱
    email = models.EmailField(
        max_length=255,
        null=True,
        blank=True,
        help_text="邮箱地址",
        validators=[EmailValidator(message="请输入有效的邮箱地址")],
        db_index=True,
    )
    
    # 手机号
    mobile = models.CharField(
        max_length=11,
        null=True,
        blank=True,
        help_text="手机号码",
        validators=[
            RegexValidator(
                regex=r'^1[3-9]\d{9}$',
                message='请输入有效的11位手机号码',
            )
        ],
        db_index=True,
    )
    
    # 头像（UUID，关联到文件存储系统）
    avatar = models.CharField(
        max_length=36,
        null=True,
        blank=True,
        help_text="用户头像UUID",
    )
    
    # 真实姓名
    name = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        help_text="真实姓名",
        db_index=True,
    )
    
    # 性别
    gender = models.IntegerField(
        choices=GENDER_CHOICES,
        default=0,
        null=True,
        blank=True,
        help_text="性别",
    )
    
    # 用户类型
    user_type = models.IntegerField(
        choices=USER_TYPE_CHOICES,
        default=1,
        help_text="用户类型",
        db_index=True,
    )
    
    # 用户状态
    user_status = models.IntegerField(
        choices=STATUS_CHOICES,
        default=1,
        help_text="用户状态",
        db_index=True,
    )
    
    # 生日
    birthday = models.DateField(
        null=True,
        blank=True,
        help_text="生日",
    )
    
    # 所在城市
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="所在城市",
    )
    
    # 地址
    address = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="详细地址",
    )
    
    # 个人简介
    bio = models.TextField(
        blank=True,
        null=True,
        help_text="个人简介",
    )


    # 最后登录IP
    last_login_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="最后登录IP",
    )
    
    # OAuth 相关字段
    oauth_provider = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="OAuth 提供商 (gitee/github/wechat 等)",
        db_index=True,
    )
    
    gitee_id = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        unique=True,
        help_text="Gitee 用户 ID",
        db_index=True,
    )
    
    github_id = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        unique=True,
        help_text="GitHub 用户 ID",
        db_index=True,
    )
    
    qq_id = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        unique=True,
        help_text="QQ 用户 openid",
        db_index=True,
    )
    
    google_id = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        unique=True,
        help_text="Google 用户 ID",
        db_index=True,
    )
    
    wechat_unionid = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        unique=True,
        help_text="微信 UnionID (跨应用唯一)",
        db_index=True,
    )
    
    wechat_openid = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        help_text="微信 OpenID (当前应用)",
        db_index=True,
    )
    
    microsoft_id = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        unique=True,
        help_text="Microsoft 用户 ID (GUID)",
        db_index=True,
    )
    
    # 钉钉用户 ID
    dingtalk_unionid = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        unique=True,
        help_text="钉钉 UnionID",
        db_index=True,
    )
    
    # 飞书用户 ID
    feishu_union_id = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        unique=True,
        help_text="飞书 Union ID",
        db_index=True,
    )
    
    # 最后登录方式
    last_login_type = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text="最后登录方式 (password/code/qrcode/gitee/github/qq/google/wechat/microsoft/dingtalk/feishu)",
        db_index=True,
    )
    
    # 关联的岗位
    post = models.ManyToManyField(
        to="core.Post",
        db_constraint=False,
        blank=True,
        help_text="关联的岗位",
        related_name="core_users",
    )
    
    # 关联的角色（使用 core.Role）
    core_roles = models.ManyToManyField(
        to="core.Role",
        db_constraint=False,
        blank=True,
        help_text="关联的角色",
        related_name="core_users",
    )
    
    # 关联的部门
    dept = models.ForeignKey(
        to="core.Dept",
        on_delete=models.SET_NULL,
        db_constraint=False,
        null=True,
        blank=True,
        help_text="所属部门",
        related_name="core_users",
    )

    is_active = models.BooleanField(
        default=True,
        help_text="用户是否激活",
        db_index=True,
    )
    
    # 直属上级
    manager = models.ForeignKey(
        to="self",
        on_delete=models.SET_NULL,
        db_constraint=False,
        null=True,
        blank=True,
        related_name="subordinates",
        help_text="直属上级",
    )
    
    class Meta:
        db_table = "core_user"
        ordering = ("-sys_create_datetime",)
        verbose_name = "用户"
        verbose_name_plural = verbose_name
        indexes = [
            models.Index(fields=['user_status', 'user_type']),
            models.Index(fields=['dept', 'user_status']),
            models.Index(fields=['is_superuser', 'user_status']),
        ]
    
    def __str__(self):
        return f"{self.name or self.username} ({self.username})"
    
    def is_active_user(self):
        """判断用户是否为正常状态"""
        return self.user_status == 1
    
    def is_locked(self):
        """判断用户是否被锁定"""
        return self.user_status == 2
    
    def is_disabled(self):
        """判断用户是否被禁用"""
        return self.user_status == 0
    
    def get_user_type_display_name(self):
        """获取用户类型的显示名称"""
        type_map = dict(self.USER_TYPE_CHOICES)
        return type_map.get(self.user_type, 'UNKNOWN')
    
    def get_user_status_display_name(self):
        """获取用户状态的显示名称"""
        status_map = dict(self.STATUS_CHOICES)
        return status_map.get(self.user_status, 'UNKNOWN')
    
    def get_gender_display_name(self):
        """获取性别的显示名称"""
        gender_map = dict(self.GENDER_CHOICES)
        return gender_map.get(self.gender, '未知')
    
    def get_role_names(self):
        """获取用户的所有角色名称"""
        return [role.name for role in self.core_roles.all()]
    
    def get_post_names(self):
        """获取用户的所有岗位名称"""
        return [post.name for post in self.post.all()]
    
    def has_permission(self, permission_code):
        """检查用户是否拥有指定权限"""
        # 超级管理员拥有所有权限
        if self.is_superuser:
            return True
        
        # 检查用户的角色是否包含该权限
        return self.core_roles.filter(
            permission__code=permission_code,
            status=True
        ).exists()
    
    def get_all_permissions(self):
        """获取用户的所有权限"""
        if self.is_superuser:
            from core.permission.permission_model import Permission
            return Permission.objects.all()
        
        # 获取用户所有角色的权限
        from core.permission.permission_model import Permission
        return Permission.objects.filter(
            roles__in=self.core_roles.filter(status=True)
        ).distinct()
    
    def get_subordinate_users(self, include_self=False):
        """获取下属用户列表"""
        users = list(self.subordinates.all())
        if include_self:
            users.insert(0, self)
        return users
    
    def can_delete(self):
        """判断用户是否可以删除（系统用户和超级管理员不能删除）"""
        return self.user_type != 0 and not self.is_superuser
    
    def set_password(self, raw_password):
        """设置密码（加密）"""
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password):
        """验证密码"""
        return check_password(raw_password, self.password)
    
    def save(self, *args, **kwargs):
        """重写save方法，确保密码被加密"""
        # 如果密码未加密（不以特定算法标识开头），则进行加密
        if self.password and not self.password.startswith(('pbkdf2_', 'bcrypt', 'argon2')):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

