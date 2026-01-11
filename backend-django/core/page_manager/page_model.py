"""
页面管理数据模型
"""
from django.db import models

from common.fu_model import RootModel


class PageMeta(RootModel):
    """页面元数据"""

    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('published', '已发布'),
    ]

    name = models.CharField(max_length=100, help_text='页面名称')
    code = models.CharField(max_length=100, unique=True, help_text='页面编码')
    category = models.CharField(max_length=50, blank=True, default='', help_text='分类')
    description = models.TextField(blank=True, default='', help_text='描述')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', help_text='状态')
    version = models.IntegerField(default=1, help_text='版本号')

    # 页面配置（存储 dashboard-design 的配置）
    page_config = models.JSONField(default=dict, help_text='页面设计配置')

    class Meta:
        db_table = 'page_meta'
        verbose_name = '页面元数据'
        verbose_name_plural = verbose_name
        ordering = ['sort', '-sys_create_datetime']

    def __str__(self):
        return f'{self.name} ({self.code})'
