"""
页面元数据管理服务
"""
import logging
from typing import Any, Dict, List

from django.db import transaction

from .page_model import PageMeta

logger = logging.getLogger(__name__)


class PageServiceException(Exception):
    """页面服务异常"""
    pass


class PageService:
    """页面元数据管理服务"""

    # ============ 查询 ============

    @staticmethod
    def list(
            page: int = 1,
            page_size: int = 20,
            name: str = None,
            code: str = None,
            category: str = None,
            status: str = None
    ) -> Dict[str, Any]:
        """
        分页查询页面列表
        
        Args:
            page: 页码
            page_size: 每页条数
            name: 页面名称（模糊）
            code: 页面编码（模糊）
            category: 分类
            status: 状态
            
        Returns:
            {items: [...], total: int, page: int, page_size: int}
        """
        queryset = PageMeta.objects.filter(is_deleted=False)

        # 过滤条件
        if name:
            queryset = queryset.filter(name__icontains=name)
        if code:
            queryset = queryset.filter(code__icontains=code)
        if category:
            queryset = queryset.filter(category=category)
        if status:
            queryset = queryset.filter(status=status)

        # 排序
        queryset = queryset.order_by('sort', '-sys_create_datetime')

        # 分页
        total = queryset.count()
        offset = (page - 1) * page_size
        items = list(queryset[offset:offset + page_size])

        return {
            'items': items,
            'total': total,
            'page': page,
            'page_size': page_size
        }

    @staticmethod
    def get(page_id: str) -> PageMeta:
        """获取页面详情"""
        try:
            return PageMeta.objects.get(id=page_id, is_deleted=False)
        except PageMeta.DoesNotExist:
            raise PageServiceException(f"页面不存在: {page_id}")

    @staticmethod
    def get_by_code(code: str) -> PageMeta:
        """根据编码获取页面"""
        try:
            return PageMeta.objects.get(code=code, is_deleted=False)
        except PageMeta.DoesNotExist:
            raise PageServiceException(f"页面不存在: {code}")

    # ============ 创建 ============

    @staticmethod
    def create(data: Dict[str, Any], user_id: str = None) -> PageMeta:
        """
        创建页面
        
        Args:
            data: 页面数据
            user_id: 创建人ID
            
        Returns:
            创建的页面对象
        """
        # 检查编码唯一性
        code = data.get('code')
        if PageMeta.objects.filter(code=code, is_deleted=False).exists():
            raise PageServiceException(f"页面编码已存在: {code}")

        with transaction.atomic():
            page = PageMeta.objects.create(
                name=data.get('name'),
                code=code,
                category=data.get('category', ''),
                description=data.get('description', ''),
                page_config=data.get('page_config', {}),
                sort=data.get('sort', 0),
                sys_creator_id=user_id
            )

            logger.info(f"页面创建成功: {page.code}")
            return page

    # ============ 更新 ============

    @staticmethod
    def update(page_id: str, data: Dict[str, Any], user_id: str = None) -> PageMeta:
        """
        更新页面
        
        Args:
            page_id: 页面ID
            data: 更新数据
            user_id: 修改人ID
            
        Returns:
            更新后的页面对象
        """
        page = PageService.get(page_id)

        with transaction.atomic():
            # 更新基本字段
            if 'name' in data and data['name'] is not None:
                page.name = data['name']
            if 'category' in data and data['category'] is not None:
                page.category = data['category']
            if 'description' in data and data['description'] is not None:
                page.description = data['description']
            if 'sort' in data and data['sort'] is not None:
                page.sort = data['sort']
            if 'page_config' in data and data['page_config'] is not None:
                page.page_config = data['page_config']

            page.sys_modifier_id = user_id
            page.save()

            logger.info(f"页面更新成功: {page.code}")
            return page

    # ============ 删除 ============

    @staticmethod
    def delete(page_id: str) -> bool:
        """
        删除页面（软删除）
        
        Args:
            page_id: 页面ID
            
        Returns:
            是否成功
        """
        page = PageService.get(page_id)

        with transaction.atomic():
            page.is_deleted = True
            page.save(update_fields=['is_deleted', 'sys_update_datetime'])

            logger.info(f"页面删除成功: {page.code}")
            return True

    @staticmethod
    def batch_delete(page_ids: List[str]) -> int:
        """
        批量删除页面
        
        Args:
            page_ids: 页面ID列表
            
        Returns:
            删除数量
        """
        with transaction.atomic():
            count = PageMeta.objects.filter(id__in=page_ids, is_deleted=False).update(is_deleted=True)

            logger.info(f"批量删除页面成功: {count} 个")
            return count

    # ============ 发布/取消发布 ============

    @staticmethod
    def publish(page_id: str, publish_config: Dict[str, Any] = None) -> PageMeta:
        """
        发布页面并创建菜单
        
        Args:
            page_id: 页面ID
            publish_config: 发布配置，包含菜单配置
        """
        from core.menu.menu_model import Menu
        from common.fu_cache import MenuCacheManager

        page = PageService.get(page_id)

        if page.status == 'published':
            raise PageServiceException("页面已发布")

        with transaction.atomic():
            # 更新页面状态
            page.status = 'published'
            page.version += 1
            page.save(update_fields=['status', 'version', 'sys_update_datetime'])

            # 创建菜单
            if publish_config:
                menu_parent_id = publish_config.get('menu_parent_id')
                parent = None
                menu_path = f'/page-render/{page.code}'

                if menu_parent_id:
                    try:
                        parent = Menu.objects.get(id=menu_parent_id)
                    except Menu.DoesNotExist:
                        pass

                # 检查是否已存在该页面的菜单（按 pageCode 查找）
                existing_menu = Menu.objects.filter(
                    query__pageCode=page.code
                ).first()

                # 如果没找到，再按原路径查找
                if not existing_menu:
                    existing_menu = Menu.objects.filter(
                        path=f'/page-render/{page.code}'
                    ).first()

                if existing_menu:
                    # 更新现有菜单
                    existing_menu.name = publish_config.get('menu_name', page.name)
                    existing_menu.title = publish_config.get('menu_name', page.name)
                    existing_menu.path = menu_path
                    existing_menu.parent = parent
                    existing_menu.icon = publish_config.get('menu_icon', 'lucide:layout-dashboard')
                    existing_menu.order = publish_config.get('menu_order', 0)
                    existing_menu.type = 'online_page'
                    existing_menu.save()
                    logger.info(f"更新页面菜单: {page.code}, path={menu_path}")
                else:
                    # 创建新菜单
                    Menu.objects.create(
                        name=publish_config.get('menu_name', page.name),
                        title=publish_config.get('menu_name', page.name),
                        path=menu_path,
                        component='_core/page-render/index',
                        type='online_page',
                        parent=parent,
                        icon=publish_config.get('menu_icon', 'lucide:layout-dashboard'),
                        order=publish_config.get('menu_order', 0),
                        query={'pageCode': page.code},
                    )
                    logger.info(f"创建页面菜单: {page.code}, path={menu_path}")

            # 清除菜单缓存
            MenuCacheManager.invalidate_menu_cache()

        logger.info(f"页面发布成功: {page.code}, version={page.version}")
        return page

    @staticmethod
    def unpublish(page_id: str) -> PageMeta:
        """取消发布页面并删除菜单"""
        from core.menu.menu_model import Menu
        from common.fu_cache import MenuCacheManager

        page = PageService.get(page_id)

        if page.status == 'draft':
            raise PageServiceException("页面未发布")

        with transaction.atomic():
            page.status = 'draft'
            page.save(update_fields=['status', 'sys_update_datetime'])

            # 删除对应菜单
            deleted_count, _ = Menu.objects.filter(
                path=f'/page-render/{page.code}'
            ).delete()

            if deleted_count > 0:
                logger.info(f"删除页面菜单: {page.code}")
                # 清除菜单缓存
                MenuCacheManager.invalidate_menu_cache()

        logger.info(f"页面取消发布: {page.code}")
        return page

    # ============ 复制 ============

    @staticmethod
    def copy(page_id: str, new_code: str, new_name: str = None, user_id: str = None) -> PageMeta:
        """
        复制页面
        
        Args:
            page_id: 源页面ID
            new_code: 新页面编码
            new_name: 新页面名称
            user_id: 创建人ID
            
        Returns:
            新页面对象
        """
        source = PageService.get(page_id)

        # 检查新编码唯一性
        if PageMeta.objects.filter(code=new_code, is_deleted=False).exists():
            raise PageServiceException(f"页面编码已存在: {new_code}")

        with transaction.atomic():
            new_page = PageMeta.objects.create(
                name=new_name or f"{source.name}_副本",
                code=new_code,
                category=source.category,
                description=source.description,
                status='draft',
                version=1,
                page_config=source.page_config,
                sort=source.sort,
                sys_creator_id=user_id
            )

            logger.info(f"页面复制成功: {source.code} -> {new_code}")
            return new_page

    # ============ 导入/导出 ============

    @staticmethod
    def export_config(page_id: str) -> Dict[str, Any]:
        """
        导出页面配置
        
        Args:
            page_id: 页面ID
            
        Returns:
            页面配置字典
        """
        page = PageService.get(page_id)

        return {
            'name': page.name,
            'code': page.code,
            'category': page.category,
            'description': page.description,
            'page_config': page.page_config,
        }

    @staticmethod
    def import_config(data: Dict[str, Any], user_id: str = None) -> PageMeta:
        """
        导入页面配置
        
        Args:
            data: 页面配置字典
            user_id: 创建人ID
            
        Returns:
            创建的页面对象
        """
        # 检查必要字段
        required_fields = ['name', 'code']
        for field in required_fields:
            if not data.get(field):
                raise PageServiceException(f"缺少必要字段: {field}")

        return PageService.create(data, user_id)

    # ============ 获取分类列表 ============

    @staticmethod
    def get_categories() -> List[str]:
        """获取所有分类"""
        categories = PageMeta.objects.filter(
            is_deleted=False
        ).exclude(
            category=''
        ).values_list('category', flat=True).distinct()

        return list(categories)
