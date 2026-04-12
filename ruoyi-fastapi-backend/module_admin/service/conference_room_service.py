from datetime import datetime
from typing import Any

from sqlalchemy import ColumnElement
from sqlalchemy.ext.asyncio import AsyncSession

from common.vo import PageModel, CrudResponseModel
from exceptions.exception import ServiceException
from module_admin.dao.conference_room_dao import ConferenceRoomDao
from module_admin.dao.conference_room_layout_dao import ConferenceRoomLayoutDao
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_admin.entity.vo.conference_room_vo import (
    AddConferenceRoomModel,
    ConferenceRoomDetailModel,
    ConferenceRoomLayoutModel,
    ConferenceRoomModel,
    ConferenceRoomPageQueryModel,
    DeleteConferenceRoomModel,
    EditConferenceRoomModel,
)
from utils.common_util import SqlalchemyUtil
from utils.log_util import logger


class ConferenceRoomService:
    """
    会议室管理模块服务层
    """

    @classmethod
    async def get_conference_room_list_services(
        cls,
        query_object: ConferenceRoomPageQueryModel,
        current_user: CurrentUserModel,
        db: AsyncSession,
        data_scope_sql: ColumnElement,
        is_page: bool = False,
    ) -> PageModel | list[dict[str, Any]]:
        """
        获取会议室列表信息service

        :param query_object: 查询参数对象
        :param current_user: 当前用户对象
        :param db: orm对象
        :param data_scope_sql: 数据权限对应的查询sql语句
        :param is_page: 是否开启分页
        :return: 会议室列表信息
        """
        room_list = await ConferenceRoomDao.get_conference_room_list(db, query_object, data_scope_sql, is_page)

        return room_list

    @classmethod
    async def add_conference_room_services(
        cls,
        add_room: AddConferenceRoomModel,
        current_user: CurrentUserModel,
        db: AsyncSession,
        data_scope_sql: ColumnElement,
    ) -> int:
        """
        新增会议室信息service

        :param add_room: 新增会议室对象
        :param current_user: 当前用户对象
        :param db: orm对象
        :param data_scope_sql: 数据权限对应的查询sql语句
        :return: 新增会议室的room_id
        """
        existing_room = await ConferenceRoomDao.get_conference_room_by_name(db, add_room.room_name)
        if existing_room:
            raise ServiceException(message=f'会议室名称{add_room.room_name}已存在')

        add_room.create_by = current_user.user.user_name
        add_room.create_time = datetime.now()
        add_room.update_by = current_user.user.user_name
        add_room.update_time = datetime.now()
        if add_room.status is None:
            add_room.status = '0'
        if add_room.del_flag is None:
            add_room.del_flag = '0'

        try:
            new_room = await ConferenceRoomDao.add_conference_room_dao(db, add_room)
            room_id = new_room.room_id
            await db.commit()
            return room_id
        except Exception as e:
            await db.rollback()
            raise e

    @classmethod
    async def edit_conference_room_services(
        cls,
        edit_room: EditConferenceRoomModel,
        current_user: CurrentUserModel,
        db: AsyncSession,
        data_scope_sql: ColumnElement,
    ) -> int:
        """
        编辑会议室信息service

        :param edit_room: 编辑会议室对象
        :param current_user: 当前用户对象
        :param db: orm对象
        :param data_scope_sql: 数据权限对应的查询sql语句
        :return: 编辑会议室的room_id
        """
        existing_room = await ConferenceRoomDao.get_conference_room_by_id(db, edit_room.room_id)
        if not existing_room:
            raise ServiceException(message='会议室不存在')

        if existing_room.room_name != edit_room.room_name:
            name_room = await ConferenceRoomDao.get_conference_room_by_name(db, edit_room.room_name)
            if name_room:
                raise ServiceException(message=f'会议室名称{edit_room.room_name}已存在')

        edit_room.update_by = current_user.user.user_name
        edit_room.update_time = datetime.now()

        edit_dict = edit_room.model_dump(exclude_unset=True, by_alias=False)
        edit_dict['room_id'] = edit_room.room_id

        try:
            await ConferenceRoomDao.edit_conference_room_dao(db, edit_dict)
            await db.commit()
            return edit_room.room_id
        except Exception as e:
            await db.rollback()
            raise e

    @classmethod
    async def delete_conference_room_services(
        cls,
        delete_room: DeleteConferenceRoomModel,
        current_user: CurrentUserModel,
        db: AsyncSession,
        data_scope_sql: ColumnElement,
    ) -> int:
        """
        删除会议室信息service

        :param delete_room: 删除会议室对象
        :param current_user: 当前用户对象
        :param db: orm对象
        :param data_scope_sql: 数据权限对应的查询sql语句
        :return: 删除会议室的数量
        """
        if delete_room.room_ids:
            room_id_list = delete_room.room_ids.split(',')
            delete_count = 0
            try:
                for room_id in room_id_list:
                    room_id_int = int(room_id.strip())
                    room_dict = {
                        'roomId': room_id_int,
                        'updateBy': current_user.user.user_name,
                        'updateTime': datetime.now(),
                    }
                    await ConferenceRoomDao.delete_conference_room_dao(db, ConferenceRoomModel(**room_dict))
                    await ConferenceRoomLayoutDao.delete_layout_by_room_id_dao(db, room_id_int)
                    delete_count += 1
                await db.commit()
                return delete_count
            except Exception as e:
                await db.rollback()
                raise e
        else:
            raise ServiceException(message='传入会议室ID为空')

    @classmethod
    async def get_conference_room_detail_services(
        cls,
        room_id: int,
        current_user: CurrentUserModel,
        db: AsyncSession,
        data_scope_sql: ColumnElement,
    ) -> ConferenceRoomDetailModel:
        """
        获取会议室详细信息service

        :param room_id: 会议室ID
        :param current_user: 当前用户对象
        :param db: orm对象
        :param data_scope_sql: 数据权限对应的查询sql语句
        :return: 会议室详细信息
        """
        existing_room = await ConferenceRoomDao.get_conference_room_by_id(db, room_id)
        if not existing_room:
            raise ServiceException(message='会议室不存在')

        layout_list = await ConferenceRoomLayoutDao.get_layout_list_by_room_id(db, room_id)
        layouts = [SqlalchemyUtil.serialize_result(layout, 'snake_to_camel') for layout in layout_list]

        room_data = SqlalchemyUtil.serialize_result(existing_room, 'snake_to_camel')

        return ConferenceRoomDetailModel(data=room_data, layouts=layouts)

    @classmethod
    async def change_conference_room_status_services(
        cls,
        room: ConferenceRoomModel,
        current_user: CurrentUserModel,
        db: AsyncSession,
        data_scope_sql: ColumnElement,
    ) -> int:
        """
        修改会议室状态service

        :param room: 会议室对象
        :param current_user: 当前用户对象
        :param db: orm对象
        :param data_scope_sql: 数据权限对应的查询sql语句
        :return: 修改会议室的room_id
        """
        existing_room = await ConferenceRoomDao.get_conference_room_by_id(db, room.room_id)
        if not existing_room:
            raise ServiceException(message='会议室不存在')

        room.update_by = current_user.user.user_name
        room.update_time = datetime.now()

        edit_dict = {
            'room_id': room.room_id,
            'status': room.status,
            'update_by': room.update_by,
            'update_time': room.update_time,
        }

        try:
            await ConferenceRoomDao.edit_conference_room_dao(db, edit_dict)
            await db.commit()
            return room.room_id
        except Exception as e:
            await db.rollback()
            raise e

    @classmethod
    async def export_conference_room_list_services(
        cls,
        query_object: ConferenceRoomPageQueryModel,
        current_user: CurrentUserModel,
        db: AsyncSession,
        data_scope_sql: ColumnElement,
    ) -> list[dict[str, Any]]:
        """
        导出会议室列表信息service

        :param query_object: 查询参数对象
        :param current_user: 当前用户对象
        :param db: orm对象
        :param data_scope_sql: 数据权限对应的查询sql语句
        :return: 会议室列表信息
        """
        room_list = await ConferenceRoomDao.get_conference_room_list(db, query_object, data_scope_sql, is_page=False)

        return room_list