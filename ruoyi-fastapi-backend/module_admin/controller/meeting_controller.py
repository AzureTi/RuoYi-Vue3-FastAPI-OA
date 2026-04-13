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
from common.vo import DataResponseModel, PageResponseModel, ResponseBaseModel
from module_admin.entity.do.meeting_do import SysMeeting
from module_admin.entity.vo.meeting_vo import (
    AddMeetingModel,
    MeetingDetailModel,
    MeetingModel,
    MeetingPageQueryModel,
    EditMeetingModel,
    DeleteMeetingModel,
)
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_admin.service.meeting_service import MeetingService
from utils.common_util import bytes2file_response, SqlalchemyUtil
from utils.log_util import logger
from utils.response_util import ResponseUtil

meeting_controller = APIRouterPro(
    prefix='/system/meeting',
    order_num=5,
    tags=['系统管理-会议管理'],
    dependencies=[PreAuthDependency()],
)


@meeting_controller.get(
    '/list',
    summary='获取会议分页列表接口',
    description='用于获取会议分页列表',
    response_model=PageResponseModel[MeetingModel],
    dependencies=[UserInterfaceAuthDependency('system:meeting:list')],
)
async def get_meeting_list(
    request: Request,
    meeting_page_query: Annotated[MeetingPageQueryModel, Query()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
    data_scope_sql: Annotated[ColumnElement, DataScopeDependency(SysMeeting)],
) -> Response:
    meeting_page_query_result = await MeetingService.get_meeting_list_services(
        meeting_page_query, current_user, query_db, data_scope_sql, is_page=True
    )
    logger.info('获取成功')

    return ResponseUtil.success(model_content=meeting_page_query_result)


@meeting_controller.get(
    '/{meeting_id}',
    summary='获取会议详情接口',
    description='用于获取会议详情',
    response_model=DataResponseModel[MeetingDetailModel],
    dependencies=[UserInterfaceAuthDependency('system:meeting:query')],
)
async def get_meeting_detail(
    request: Request,
    meeting_id: Annotated[int, Path(description='会议ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    meeting_detail_result = await MeetingService.get_meeting_detail_services(query_db, meeting_id)
    logger.info('获取成功')

    return ResponseUtil.success(data=meeting_detail_result)


@meeting_controller.post(
    '',
    summary='新增会议接口',
    description='用于新增会议',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('system:meeting:add')],
)
@ValidateFields(validate_model='add_meeting')
@Log(title='会议管理', business_type=BusinessType.INSERT)
async def add_meeting(
    request: Request,
    add_meeting: AddMeetingModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
    data_scope_sql: Annotated[ColumnElement, DataScopeDependency(SysMeeting)],
) -> Response:
    add_meeting_result = await MeetingService.add_meeting_services(
        add_meeting, current_user, query_db, data_scope_sql
    )
    logger.info(f'新增会议成功，会议ID：{add_meeting_result}')

    return ResponseUtil.success(msg='新增会议成功')


@meeting_controller.put(
    '',
    summary='编辑会议接口',
    description='用于编辑会议',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('system:meeting:edit')],
)
@ValidateFields(validate_model='edit_meeting')
@Log(title='会议管理', business_type=BusinessType.UPDATE)
async def edit_meeting(
    request: Request,
    edit_meeting: EditMeetingModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
    data_scope_sql: Annotated[ColumnElement, DataScopeDependency(SysMeeting)],
) -> Response:
    edit_meeting_result = await MeetingService.edit_meeting_services(
        edit_meeting, current_user, query_db, data_scope_sql
    )
    logger.info(f'编辑会议成功，会议ID：{edit_meeting_result}')

    return ResponseUtil.success(msg='编辑会议成功')


@meeting_controller.delete(
    '/{meeting_ids}',
    summary='删除会议接口',
    description='用于删除会议',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('system:meeting:remove')],
)
@Log(title='会议管理', business_type=BusinessType.DELETE)
async def delete_meeting(
    request: Request,
    meeting_ids: Annotated[str, Path(description='需要删除的会议ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    delete_meeting_result = await MeetingService.delete_meeting_services(
        meeting_ids, current_user, query_db
    )
    logger.info('删除成功')

    return ResponseUtil.success(msg=delete_meeting_result.message)
