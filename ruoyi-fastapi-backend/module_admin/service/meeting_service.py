from datetime import datetime
from typing import Any

from sqlalchemy import ColumnElement
from sqlalchemy.ext.asyncio import AsyncSession

from common.vo import PageModel, CrudResponseModel
from exceptions.exception import ServiceException
from module_admin.dao.meeting_dao import MeetingDao
from module_admin.dao.conference_room_dao import ConferenceRoomDao
from module_admin.entity.do.meeting_do import SysMeeting
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_admin.entity.vo.meeting_vo import (
    AddMeetingModel,
    MeetingDetailModel,
    MeetingModel,
    MeetingPageQueryModel,
    EditMeetingModel,
)
from utils.log_util import logger
from utils.common_util import SqlalchemyUtil


class MeetingService:
    """
    会议管理模块服务层
    """

    @classmethod
    async def get_meeting_list_services(
        cls,
        query_object: MeetingPageQueryModel,
        current_user: CurrentUserModel,
        db: AsyncSession,
        data_scope_sql: ColumnElement,
        is_page: bool = False,
    ) -> PageModel | list[dict[str, Any]]:
        """
        获取会议列表信息service

        :param query_object: 查询参数对象
        :param current_user: 当前用户对象
        :param db: orm对象
        :param data_scope_sql: 数据权限对应的查询sql语句
        :param is_page: 是否开启分页
        :return: 会议列表信息
        """
        meeting_list = await MeetingDao.get_meeting_list(db, query_object, data_scope_sql, is_page)

        # 为每个会议添加主会场名称
        if is_page and hasattr(meeting_list, 'rows'):
            for meeting in meeting_list.rows:
                if meeting.get('mainRoomId'):
                    main_room = await ConferenceRoomDao.get_conference_room_by_id(db, meeting['mainRoomId'])
                    if main_room:
                        meeting['mainRoomName'] = main_room.room_name
                    else:
                        meeting['mainRoomName'] = None
                else:
                    meeting['mainRoomName'] = None
        elif not is_page and isinstance(meeting_list, list):
            for meeting in meeting_list:
                if meeting.get('mainRoomId'):
                    main_room = await ConferenceRoomDao.get_conference_room_by_id(db, meeting['mainRoomId'])
                    if main_room:
                        meeting['mainRoomName'] = main_room.room_name
                    else:
                        meeting['mainRoomName'] = None
                else:
                    meeting['mainRoomName'] = None

        return meeting_list

    @classmethod
    async def get_meeting_detail_services(
        cls,
        db: AsyncSession,
        meeting_id: int,
    ) -> MeetingDetailModel:
        """
        获取会议详情service

        :param db: orm对象
        :param meeting_id: 会议ID
        :return: 会议详情
        """
        meeting = await MeetingDao.get_meeting_by_id(db, meeting_id)
        if not meeting:
            raise ServiceException(message='会议不存在')

        meeting_data = SqlalchemyUtil.serialize_result(meeting, 'snake_to_camel')

        main_room_name = None
        sub_room_names = []

        if meeting.main_room_id:
            main_room = await ConferenceRoomDao.get_conference_room_by_id(db, meeting.main_room_id)
            if main_room:
                main_room_name = main_room.room_name

        if meeting.sub_rooms:
            sub_room_ids = [int(rid.strip()) for rid in meeting.sub_rooms.split(',') if rid.strip()]
            for sub_room_id in sub_room_ids:
                sub_room = await ConferenceRoomDao.get_conference_room_by_id(db, sub_room_id)
                if sub_room:
                    sub_room_names.append(sub_room.room_name)

        return MeetingDetailModel(
            data=meeting_data,
            main_room_name=main_room_name,
            sub_room_names=sub_room_names,
        )

    @classmethod
    async def add_meeting_services(
        cls,
        add_meeting: AddMeetingModel,
        current_user: CurrentUserModel,
        db: AsyncSession,
        data_scope_sql: ColumnElement,
    ) -> int:
        """
        新增会议信息service

        :param add_meeting: 新增会议对象
        :param current_user: 当前用户对象
        :param db: orm对象
        :param data_scope_sql: 数据权限对应的查询sql语句
        :return: 新增会议的meeting_id
        """
        add_meeting.create_by = current_user.user.user_name
        add_meeting.create_time = datetime.now()
        add_meeting.update_by = current_user.user.user_name
        add_meeting.update_time = datetime.now()
        if add_meeting.status is None:
            add_meeting.status = '0'
        if add_meeting.del_flag is None:
            add_meeting.del_flag = '0'

        new_meeting = SysMeeting(
            meeting_name=add_meeting.meeting_name,
            dept_id=add_meeting.dept_id,
            main_room_id=add_meeting.main_room_id,
            sub_rooms=add_meeting.sub_rooms,
            start_time=add_meeting.start_time,
            duration=add_meeting.duration,
            status=add_meeting.status,
            organizer_id=add_meeting.organizer_id,
            del_flag=add_meeting.del_flag,
            create_by=add_meeting.create_by,
            create_time=add_meeting.create_time,
            update_by=add_meeting.update_by,
            update_time=add_meeting.update_time,
            remark=add_meeting.remark,
        )

        try:
            saved_meeting = await MeetingDao.add_meeting_dao(db, new_meeting)
            meeting_id = saved_meeting.meeting_id
            await db.commit()
            return meeting_id
        except Exception as e:
            await db.rollback()
            raise e

    @classmethod
    async def edit_meeting_services(
        cls,
        edit_meeting: EditMeetingModel,
        current_user: CurrentUserModel,
        db: AsyncSession,
        data_scope_sql: ColumnElement,
    ) -> int:
        """
        编辑会议信息service

        :param edit_meeting: 编辑会议对象
        :param current_user: 当前用户对象
        :param db: orm对象
        :param data_scope_sql: 数据权限对应的查询sql语句
        :return: 编辑会议的meeting_id
        """
        existing_meeting = await MeetingDao.get_meeting_by_id(db, edit_meeting.meeting_id)
        if not existing_meeting:
            raise ServiceException(message='会议不存在')

        edit_meeting.update_by = current_user.user.user_name
        edit_meeting.update_time = datetime.now()

        update_data = {
            'meeting_id': edit_meeting.meeting_id,
            'meeting_name': edit_meeting.meeting_name,
            'dept_id': edit_meeting.dept_id,
            'main_room_id': edit_meeting.main_room_id,
            'sub_rooms': edit_meeting.sub_rooms,
            'start_time': edit_meeting.start_time,
            'duration': edit_meeting.duration,
            'status': edit_meeting.status,
            'organizer_id': edit_meeting.organizer_id,
            'update_by': edit_meeting.update_by,
            'update_time': edit_meeting.update_time,
            'remark': edit_meeting.remark,
        }

        try:
            await MeetingDao.edit_meeting_dao(db, update_data)
            await db.commit()
            return edit_meeting.meeting_id
        except Exception as e:
            await db.rollback()
            raise e

    @classmethod
    async def delete_meeting_services(
        cls,
        meeting_ids: str,
        current_user: CurrentUserModel,
        db: AsyncSession,
    ) -> CrudResponseModel:
        """
        删除会议信息service

        :param meeting_ids: 需要删除的会议ID
        :param current_user: 当前用户对象
        :param db: orm对象
        :return: 删除结果
        """
        if meeting_ids:
            meeting_id_list = meeting_ids.split(',')
            try:
                for meeting_id in meeting_id_list:
                    await MeetingDao.delete_meeting_dao(db, int(meeting_id))
                await db.commit()
                return CrudResponseModel(is_success=True, message='删除成功')
            except Exception as e:
                await db.rollback()
                raise e
        else:
            raise ServiceException(message='传入会议id为空')
