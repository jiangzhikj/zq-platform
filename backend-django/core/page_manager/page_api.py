"""
页面管理 API
页面元数据的 CRUD、发布、复制、导入导出
"""
import json
import logging
from typing import List

from django.http import HttpResponse
from ninja import Query, Router
from ninja.errors import HttpError
from ninja.pagination import paginate

from common.fu_pagination import MyPagination
from .page_schema import (
    PageImportIn,
    PageMetaCreateIn,
    PageMetaListOut,
    PageMetaOut,
    PageMetaUpdateIn,
    PagePublishIn,
)
from .page_service import PageService, PageServiceException

logger = logging.getLogger(__name__)

router = Router(tags=['页面管理'])


# ============ 页面元数据 CRUD ============

@router.get('/list', response=List[PageMetaListOut], summary='页面列表')
@paginate(MyPagination)
def list_pages(
        request,
        name: str = Query(None, description='页面名称'),
        code: str = Query(None, description='页面编码'),
        category: str = Query(None, description='分类'),
        status: str = Query(None, description='状态')
):
    """分页查询页面列表"""
    result = PageService.list(
        page=getattr(request, 'page', 1),
        page_size=getattr(request, 'page_size', 20),
        name=name,
        code=code,
        category=category,
        status=status
    )
    return result['items']


@router.get('/categories', response=List[str], summary='获取分类列表')
def get_categories(request):
    """获取所有页面分类"""
    return PageService.get_categories()


@router.get('/code/{code}', response=PageMetaOut, summary='根据编码获取页面')
def get_page_by_code(request, code: str):
    """根据编码获取页面详情"""
    try:
        return PageService.get_by_code(code)
    except PageServiceException as e:
        raise HttpError(400, str(e))


@router.get('/{page_id}', response=PageMetaOut, summary='页面详情')
def get_page(request, page_id: str):
    """获取页面详情"""
    try:
        return PageService.get(page_id)
    except PageServiceException as e:
        raise HttpError(400, str(e))


@router.post('', response=PageMetaOut, summary='创建页面')
def create_page(request, data: PageMetaCreateIn):
    """创建页面"""
    user_info = request.auth
    user_id = user_info.id if user_info else None

    try:
        return PageService.create(data.dict(), user_id)
    except PageServiceException as e:
        raise HttpError(400, str(e))


@router.put('/{page_id}', response=PageMetaOut, summary='更新页面')
def update_page(request, page_id: str, data: PageMetaUpdateIn):
    """更新页面"""
    user_info = request.auth
    user_id = user_info.id if user_info else None

    try:
        return PageService.update(page_id, data.dict(exclude_none=True), user_id)
    except PageServiceException as e:
        raise HttpError(400, str(e))


@router.delete('/{page_id}', response=PageMetaOut, summary='删除页面')
def delete_page(request, page_id: str):
    """删除页面"""
    try:
        page = PageService.get(page_id)
        PageService.delete(page_id)
        return page
    except PageServiceException as e:
        raise HttpError(400, str(e))


@router.delete('/batch', summary='批量删除页面')
def batch_delete_pages(request, ids: List[str] = Query(...)):
    """批量删除页面"""
    count = PageService.batch_delete(ids)
    return {'count': count}


# ============ 发布/取消发布 ============

@router.post('/{page_id}/publish', response=PageMetaOut, summary='发布页面')
def publish_page(request, page_id: str, data: PagePublishIn):
    """发布页面并创建菜单"""
    try:
        return PageService.publish(page_id, data.dict())
    except PageServiceException as e:
        raise HttpError(400, str(e))


@router.post('/{page_id}/unpublish', response=PageMetaOut, summary='取消发布')
def unpublish_page(request, page_id: str):
    """取消发布页面并删除菜单"""
    try:
        return PageService.unpublish(page_id)
    except PageServiceException as e:
        raise HttpError(400, str(e))


# ============ 复制 ============

@router.post('/{page_id}/copy', response=PageMetaOut, summary='复制页面')
def copy_page(
        request,
        page_id: str,
        new_code: str = Query(..., description='新页面编码'),
        new_name: str = Query(None, description='新页面名称')
):
    """复制页面"""
    user_info = request.auth
    user_id = user_info.id if user_info else None

    try:
        return PageService.copy(page_id, new_code, new_name, user_id)
    except PageServiceException as e:
        raise HttpError(400, str(e))


# ============ 导入/导出配置 ============

@router.get('/{page_id}/export', summary='导出页面配置')
def export_page_config(request, page_id: str):
    """导出页面配置为 JSON"""
    try:
        config = PageService.export_config(page_id)

        # 返回 JSON 文件
        response = HttpResponse(
            json.dumps(config, ensure_ascii=False, indent=2),
            content_type='application/json'
        )
        response['Content-Disposition'] = f'attachment; filename="{config["code"]}.json"'
        return response
    except PageServiceException as e:
        raise HttpError(400, str(e))


@router.post('/import', response=PageMetaOut, summary='导入页面配置')
def import_page_config(request, data: PageImportIn):
    """导入页面配置"""
    user_info = request.auth
    user_id = user_info.id if user_info else None

    try:
        return PageService.import_config(data.dict(), user_id)
    except PageServiceException as e:
        raise HttpError(400, str(e))
