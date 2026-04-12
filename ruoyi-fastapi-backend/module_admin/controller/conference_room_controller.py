from datetime import datetime
from typing import Annotated

from fastapi import Path, Query, Request, Response
from pydantic_validation_decorator import ValidateFields
from sqlalchemy import ColumnElement
from sqlalchemy.ext.asyncio import AsyncSession

from common.annotation.log_annotation import Log
from common.aspect.data_scope import DataScopeDependency
from common.aspect.db_seesion import DBSessionDependency
from common.aspect.interface_auth import UserInterfaceAuthDependency
from common.aspect.pre_auth import CurrentUserDependency, PreAuthDependency
from common.constant import ApiGroup, ApiNamespace
from common.enums import BusinessType
from common.router import APIRouterPro
from common.vo import DataResponseModel, DynamicResponseModel, PageResponseModel, ResponseBaseModel
from module_admin.entity.do.conference_room_do import SysConferenceRoom
from module_admin.entity.vo.conference_room_vo import (
    AddConferenceRoomLayoutModel,
    AddConferenceRoomModel,
    ConferenceRoomDetailModel,
    ConferenceRoomLayoutModel,
    ConferenceRoomLayoutQueryModel,
    ConferenceRoomModel,
    ConferenceRoomPageQueryModel,
    DeleteConferenceRoomLayoutModel,
    DeleteConferenceRoomModel,
    EditConferenceRoomLayoutModel,
    EditConferenceRoomModel,
)
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_admin.service.conference_room_layout_service import ConferenceRoomLayoutService
from module_admin.service.conference_room_service import ConferenceRoomService
from utils.common_util import bytes2file_response, SqlalchemyUtil
from utils.log_util import logger
from utils.response_util import ResponseUtil

conference_room_controller = APIRouterPro(
    prefix='/system/conferenceRoom',
    order_num=4,
    tags=['系统管理-会议室管理'],
    dependencies=[PreAuthDependency()],
)


@conference_room_controller.get(
    '/list',
    summary='获取会议室分页列表接口',
    description='用于获取会议室分页列表',
    response_model=PageResponseModel[ConferenceRoomModel],
    dependencies=[UserInterfaceAuthDependency('system:conferenceRoom:list')],
)
async def get_conference_room_list(
    request: Request,
    room_page_query: Annotated[ConferenceRoomPageQueryModel, Query()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
    data_scope_sql: Annotated[ColumnElement, DataScopeDependency(SysConferenceRoom)],
) -> Response:
    room_page_query_result = await ConferenceRoomService.get_conference_room_list_services(
        room_page_query, current_user, query_db, data_scope_sql, is_page=True
    )
    logger.info('获取成功')

    return ResponseUtil.success(model_content=room_page_query_result)


@conference_room_controller.post(
    '',
    summary='新增会议室接口',
    description='用于新增会议室',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('system:conferenceRoom:add')],
)
@ValidateFields(validate_model='add_room')
@Log(title='会议室管理', business_type=BusinessType.INSERT)
async def add_conference_room(
    request: Request,
    add_room: AddConferenceRoomModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
    data_scope_sql: Annotated[ColumnElement, DataScopeDependency(SysConferenceRoom)],
) -> Response:
    add_room_result = await ConferenceRoomService.add_conference_room_services(
        add_room, current_user, query_db, data_scope_sql
    )
    logger.info(f'新增会议室成功，会议室ID：{add_room_result}')

    return ResponseUtil.success(msg='新增会议室成功')


@conference_room_controller.put(
    '',
    summary='编辑会议室接口',
    description='用于编辑会议室',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('system:conferenceRoom:edit')],
)
@ValidateFields(validate_model='edit_room')
@Log(title='会议室管理', business_type=BusinessType.UPDATE)
async def edit_conference_room(
    request: Request,
    edit_room: EditConferenceRoomModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
    data_scope_sql: Annotated[ColumnElement, DataScopeDependency(SysConferenceRoom)],
) -> Response:
    edit_room_result = await ConferenceRoomService.edit_conference_room_services(
        edit_room, current_user, query_db, data_scope_sql
    )
    logger.info(f'编辑会议室成功，会议室ID：{edit_room_result}')

    return ResponseUtil.success(msg='编辑会议室成功')


@conference_room_controller.delete(
    '/{room_ids}',
    summary='删除会议室接口',
    description='用于删除会议室',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('system:conferenceRoom:remove')],
)
@Log(title='会议室管理', business_type=BusinessType.DELETE)
async def delete_conference_room(
    request: Request,
    room_ids: Annotated[str, Path(description='需要删除的会议室ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
    data_scope_sql: Annotated[ColumnElement, DataScopeDependency(SysConferenceRoom)],
) -> Response:
    delete_room = DeleteConferenceRoomModel(
        roomIds=room_ids, updateBy=current_user.user.user_name, updateTime=datetime.now()
    )
    delete_room_result = await ConferenceRoomService.delete_conference_room_services(
        delete_room, current_user, query_db, data_scope_sql
    )
    logger.info(f'删除会议室成功，删除数量：{delete_room_result}')

    return ResponseUtil.success(msg='删除会议室成功')


@conference_room_controller.get(
    '/{room_id}',
    summary='获取会议室详细信息接口',
    description='用于获取会议室详细信息',
    response_model=DataResponseModel[ConferenceRoomDetailModel],
    dependencies=[UserInterfaceAuthDependency('system:conferenceRoom:detail')],
)
async def get_conference_room_detail(
    request: Request,
    room_id: Annotated[int, Path(description='会议室ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
    data_scope_sql: Annotated[ColumnElement, DataScopeDependency(SysConferenceRoom)],
) -> Response:
    room_detail_result = await ConferenceRoomService.get_conference_room_detail_services(
        room_id, current_user, query_db, data_scope_sql
    )
    logger.info('获取会议室详细信息成功')

    return ResponseUtil.success(data=room_detail_result)


@conference_room_controller.put(
    '/changeStatus',
    summary='修改会议室状态接口',
    description='用于修改会议室状态',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('system:conferenceRoom:edit')],
)
@Log(title='会议室管理', business_type=BusinessType.UPDATE)
async def change_conference_room_status(
    request: Request,
    room: ConferenceRoomModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
    data_scope_sql: Annotated[ColumnElement, DataScopeDependency(SysConferenceRoom)],
) -> Response:
    change_status_result = await ConferenceRoomService.change_conference_room_status_services(
        room, current_user, query_db, data_scope_sql
    )
    logger.info(f'修改会议室状态成功，会议室ID：{change_status_result}')

    return ResponseUtil.success(msg='修改会议室状态成功')


@conference_room_controller.post(
    '/export',
    summary='导出会议室列表接口',
    description='用于导出会议室列表',
    dependencies=[UserInterfaceAuthDependency('system:conferenceRoom:export')],
)
@Log(title='会议室管理', business_type=BusinessType.EXPORT)
async def export_conference_room_list(
    request: Request,
    room_query: ConferenceRoomPageQueryModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
    data_scope_sql: Annotated[ColumnElement, DataScopeDependency(SysConferenceRoom)],
) -> Response:
    room_list_result = await ConferenceRoomService.export_conference_room_list_services(
        room_query, current_user, query_db, data_scope_sql
    )
    logger.info('导出会议室列表成功')

    return ResponseUtil.success(data=room_list_result)


@conference_room_controller.get(
    '/layout/list/{room_id}',
    summary='获取会议室布局列表接口',
    description='用于获取指定会议室的布局列表',
    response_model=DataResponseModel[list[ConferenceRoomLayoutModel]],
    dependencies=[UserInterfaceAuthDependency('system:conferenceRoom:list')],
)
async def get_conference_room_layout_list(
    request: Request,
    room_id: Annotated[int, Path(description='会议室ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
    data_scope_sql: Annotated[ColumnElement, DataScopeDependency(SysConferenceRoom)],
) -> Response:
    layout_list_result = await ConferenceRoomLayoutService.get_layout_list_by_room_id_services(
        room_id, current_user, query_db, data_scope_sql
    )
    logger.info('获取会议室布局列表成功')

    return ResponseUtil.success(data=layout_list_result)


@conference_room_controller.post(
    '/layout',
    summary='新增会议室布局接口',
    description='用于新增会议室布局',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('system:conferenceRoom:add')],
)
@ValidateFields(validate_model='add_layout')
@Log(title='会议室布局管理', business_type=BusinessType.INSERT)
async def add_conference_room_layout(
    request: Request,
    add_layout: AddConferenceRoomLayoutModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
    data_scope_sql: Annotated[ColumnElement, DataScopeDependency(SysConferenceRoom)],
) -> Response:
    add_layout_result = await ConferenceRoomLayoutService.add_layout_services(
        add_layout, current_user, query_db, data_scope_sql
    )
    logger.info(f'新增会议室布局成功，布局ID：{add_layout_result}')

    return ResponseUtil.success(msg='新增会议室布局成功')


@conference_room_controller.put(
    '/layout',
    summary='编辑会议室布局接口',
    description='用于编辑会议室布局',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('system:conferenceRoom:edit')],
)
@ValidateFields(validate_model='edit_layout')
@Log(title='会议室布局管理', business_type=BusinessType.UPDATE)
async def edit_conference_room_layout(
    request: Request,
    edit_layout: EditConferenceRoomLayoutModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
    data_scope_sql: Annotated[ColumnElement, DataScopeDependency(SysConferenceRoom)],
) -> Response:
    edit_layout_result = await ConferenceRoomLayoutService.edit_layout_services(
        edit_layout, current_user, query_db, data_scope_sql
    )
    logger.info(f'编辑会议室布局成功，布局ID：{edit_layout_result}')

    return ResponseUtil.success(msg='编辑会议室布局成功')


@conference_room_controller.delete(
    '/layout/{layout_ids}',
    summary='删除会议室布局接口',
    description='用于删除会议室布局',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('system:conferenceRoom:remove')],
)
@Log(title='会议室布局管理', business_type=BusinessType.DELETE)
async def delete_conference_room_layout(
    request: Request,
    layout_ids: Annotated[str, Path(description='需要删除的布局ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
    data_scope_sql: Annotated[ColumnElement, DataScopeDependency(SysConferenceRoom)],
) -> Response:
    delete_layout = DeleteConferenceRoomLayoutModel(
        layoutIds=layout_ids, updateBy=current_user.user.user_name, updateTime=datetime.now()
    )
    delete_layout_result = await ConferenceRoomLayoutService.delete_layout_services(
        delete_layout, current_user, query_db, data_scope_sql
    )
    logger.info(f'删除会议室布局成功，删除数量：{delete_layout_result}')

    return ResponseUtil.success(msg='删除会议室布局成功')


@conference_room_controller.get(
    '/layout/{layout_id}',
    summary='获取会议室布局详细信息接口',
    description='用于获取会议室布局详细信息',
    response_model=DataResponseModel[ConferenceRoomLayoutModel],
    dependencies=[UserInterfaceAuthDependency('system:conferenceRoom:detail')],
)
async def get_conference_room_layout_detail(
    request: Request,
    layout_id: Annotated[int, Path(description='布局ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
    data_scope_sql: Annotated[ColumnElement, DataScopeDependency(SysConferenceRoom)],
) -> Response:
    layout_detail_result = await ConferenceRoomLayoutService.get_layout_detail_services(
        layout_id, current_user, query_db, data_scope_sql
    )
    logger.info('获取会议室布局详细信息成功')

    return ResponseUtil.success(data=layout_detail_result)


@conference_room_controller.get(
    '/layout/room/{room_id}',
    summary='获取会议室布局接口',
    description='用于获取指定会议室的布局信息',
    response_model=DynamicResponseModel,
    dependencies=[UserInterfaceAuthDependency('system:conferenceRoom:query')],
)
async def get_conference_room_layout_by_room_id(
    request: Request,
    room_id: Annotated[int, Path(description='会议室ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    layout_result = await ConferenceRoomLayoutService.get_conference_room_layout_services(query_db, room_id)
    logger.info(f'获取room_id为{room_id}的布局信息成功')

    return ResponseUtil.success(data=layout_result)


@conference_room_controller.post(
    '/layout/save',
    summary='保存会议室布局接口',
    description='用于保存会议室布局信息',
    response_model=DynamicResponseModel,
    dependencies=[UserInterfaceAuthDependency('system:conferenceRoom:edit')],
)
@Log(title='会议室布局管理', business_type=BusinessType.UPDATE)
async def save_conference_room_layout(
    request: Request,
    layout_data: dict,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    room_id = layout_data.get('roomId')
    if not room_id:
        return ResponseUtil.failure(msg='会议室ID不能为空')

    layout_result = await ConferenceRoomLayoutService.save_conference_room_layout_services(
        query_db, room_id, layout_data, current_user.user.user_name
    )
    logger.info(f'保存room_id为{room_id}的布局信息成功')

    return ResponseUtil.success(data=layout_result)