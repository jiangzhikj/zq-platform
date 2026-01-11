# Generated migration for page_manager

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PageMeta',
            fields=[
                ('id', models.CharField(default=uuid.uuid4, editable=False, help_text='主键ID', max_length=36,
                                        primary_key=True, serialize=False)),
                ('sys_create_datetime', models.DateTimeField(auto_now_add=True, db_index=True, help_text='创建时间')),
                ('sys_update_datetime', models.DateTimeField(auto_now=True, db_index=True, help_text='更新时间')),
                ('is_deleted', models.BooleanField(db_index=True, default=False, help_text='是否删除（软删除标识）')),
                ('sort', models.IntegerField(db_index=True, default=0, help_text='排序（数字越大越靠前）')),
                ('name', models.CharField(help_text='页面名称', max_length=100)),
                ('code', models.CharField(help_text='页面编码', max_length=100, unique=True)),
                ('category', models.CharField(blank=True, default='', help_text='分类', max_length=50)),
                ('description', models.TextField(blank=True, default='', help_text='描述')),
                ('status', models.CharField(choices=[('draft', '草稿'), ('published', '已发布')], default='draft',
                                            help_text='状态', max_length=20)),
                ('version', models.IntegerField(default=1, help_text='版本号')),
                ('page_config', models.JSONField(default=dict, help_text='页面设计配置')),
                ('sys_creator',
                 models.ForeignKey(blank=True, db_constraint=False, db_index=True, help_text='创建人', null=True,
                                   on_delete=django.db.models.deletion.SET_NULL,
                                   related_name='%(app_label)s_%(class)s_created', to='core.user')),
                ('sys_modifier', models.ForeignKey(blank=True, db_constraint=False, help_text='修改人', null=True,
                                                   on_delete=django.db.models.deletion.SET_NULL,
                                                   related_name='%(app_label)s_%(class)s_modified', to='core.user')),
            ],
            options={
                'verbose_name': '页面元数据',
                'verbose_name_plural': '页面元数据',
                'db_table': 'page_meta',
                'ordering': ['sort', '-sys_create_datetime'],
            },
        ),
    ]
