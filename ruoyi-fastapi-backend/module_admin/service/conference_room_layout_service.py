import json
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import ColumnElement
from sqlalchemy.ext.asyncio import AsyncSession

from common.vo import PageModel
from exceptions.exception import ServiceException
from module_admin.dao.conference_room_dao import ConferenceRoomDao
from module_admin.dao.conference_room_layout_dao import ConferenceRoomLayoutDao
from module_admin.entity.do.conference_room_layout_do import SysConferenceRoomLayout
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_admin.entity.vo.conference_room_vo import (
    AddConferenceRoomLayoutModel,
    ConferenceRoomLayoutModel,
    ConferenceRoomLayoutQueryModel,
    DeleteConferenceRoomLayoutModel,
    EditConferenceRoomLayoutModel,
)
from utils.common_util import SqlalchemyUtil


class ConferenceRoomLayoutService:
    """
    会议室布局管理模块服务层
    """

    @classmethod
    async def get_conference_room_layout_services(
        cls,
        db: AsyncSession,
        room_id: int
    ) -> Optional[dict]:
        """
        获取会议室布局

        :param db: 数据库会话
        :param room_id: 会议室ID
        :return: 布局信息
        """
        layout = await ConferenceRoomLayoutDao.get_conference_room_layout_by_room_id_dao(db, room_id)
        if not layout:
            return None

        result = {
            'layoutId': layout.layout_id,
            'roomId': layout.room_id,
            'config': json.loads(layout.config) if layout.config else {},
            'seats': json.loads(layout.seats) if layout.seats else [],
            'createBy': layout.create_by,
            'createTime': layout.create_time,
            'updateBy': layout.update_by,
            'updateTime': layout.update_time,
            'remark': layout.remark
        }
        return result

    @classmethod
    async def save_conference_room_layout_services(
        cls,
        db: AsyncSession,
        room_id: int,
        layout_data: dict,
        user_name: str
    ) -> dict:
        """
        保存会议室布局

        :param db: 数据库会话
        :param room_id: 会议室ID
        :param layout_data: 布局数据
        :param user_name: 操作用户
        :return: 布局信息
        """
        existing_layout = await ConferenceRoomLayoutDao.get_conference_room_layout_by_room_id_dao(db, room_id)

        layout_info = {
            'config': json.dumps(layout_data.get('config', {})),
            'seats': json.dumps(layout_data.get('seats', [])),
            'update_by': user_name
        }

        if existing_layout:
            await ConferenceRoomLayoutDao.update_conference_room_layout_dao(db, room_id, layout_info)
        else:
            new_layout = SysConferenceRoomLayout(
                room_id=room_id,
                config=layout_info['config'],
                seats=layout_info['seats'],
                create_by=user_name,
                update_by=user_name
            )
            await ConferenceRoomLayoutDao.add_conference_room_layout_dao(db, new_layout)

        try:
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise e

        layout = await ConferenceRoomLayoutDao.get_conference_room_layout_by_room_id_dao(db, room_id)
        if not layout:
            raise ServiceException(message='保存布局失败')

        result = {
            'layoutId': layout.layout_id,
            'roomId': layout.room_id,
            'config': json.loads(layout.config) if layout.config else {},
            'seats': json.loads(layout.seats) if layout.seats else [],
            'createBy': layout.create_by,
            'createTime': layout.create_time,
            'updateBy': layout.update_by,
            'updateTime': layout.update_time,
            'remark': layout.remark
        }
        return result

    @classmethod
    async def delete_conference_room_layout_services(
        cls,
        db: AsyncSession,
        room_id: int
    ) -> bool:
        """
        删除会议室布局

        :param db: 数据库会话
        :param room_id: 会议室ID
        :return: 是否删除成功
        """
        result = await ConferenceRoomLayoutDao.delete_conference_room_layout_dao(db, room_id)
        try:
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise e
        return result

    @classmethod
    async def get_layout_list_services(
        cls,
        query_object: ConferenceRoomLayoutQueryModel,
        current_user: CurrentUserModel,
        db: AsyncSession,
        data_scope_sql: ColumnElement,
        is_page: bool = False,
        page_num: int = 1,
        page_size: int = 10,
    ) -> PageModel | list[dict[str, Any]]:
        """
        获取布局列表信息service

        :param query_object: 查询参数对象
        :param current_user: 当前用户对象
        :param db: orm对象
        :param data_scope_sql: 数据权限对应的查询sql语句
        :param is_page: 是否开启分页
        :param page_num: 当前页码
        :param page_size: 每页记录数
        :return: 布局列表信息
        """
        layout_list = await ConferenceRoomLayoutDao.get_layout_list(
            db, query_object, data_scope_sql, is_page, page_num, page_size
        )

        return layout_list

    @classmethod
    async def get_layout_list_by_room_id_services(
        cls,
        room_id: int,
        current_user: CurrentUserModel,
        db: AsyncSession,
        data_scope_sql: ColumnElement,
    ) -> list[dict[str, Any]]:
        """
        根据会议室ID获取布局列表service

        :param room_id: 会议室ID
        :param current_user: 当前用户对象
        :param db: orm对象
        :param data_scope_sql: 数据权限对应的查询sql语句
        :return: 布局列表信息
        """
        existing_room = await ConferenceRoomDao.get_conference_room_by_id(db, room_id)
        if not existing_room:
            raise ServiceException(message='会议室不存在')

        layout_list = await ConferenceRoomLayoutDao.get_layout_list_by_room_id(db, room_id)
        layouts = [SqlalchemyUtil.serialize_result(layout) for layout in layout_list]

        return layouts

    @classmethod
    async def add_layout_services(
        cls,
        add_layout: AddConferenceRoomLayoutModel,
        current_user: CurrentUserModel,
        db: AsyncSession,
        data_scope_sql: ColumnElement,
    ) -> int:
        """
        新增布局信息service

        :param add_layout: 新增布局对象
        :param current_user: 当前用户对象
        :param db: orm对象
        :param data_scope_sql: 数据权限对应的查询sql语句
        :return: 新增布局的layout_id
        """
        existing_room = await ConferenceRoomDao.get_conference_room_by_id(db, add_layout.room_id)
        if not existing_room:
            raise ServiceException(message='会议室不存在')

        add_layout.create_by = current_user.user.user_name
        add_layout.create_time = datetime.now()
        add_layout.update_by = current_user.user.user_name
        add_layout.update_time = datetime.now()

        try:
            new_layout = await ConferenceRoomLayoutDao.add_layout_dao(db, add_layout)
            layout_id = new_layout.layout_id
            await db.commit()
            return layout_id
        except Exception as e:
            await db.rollback()
            raise e

    @classmethod
    async def edit_layout_services(
        cls,
        edit_layout: EditConferenceRoomLayoutModel,
        current_user: CurrentUserModel,
        db: AsyncSession,
        data_scope_sql: ColumnElement,
    ) -> int:
        """
        编辑布局信息service

        :param edit_layout: 编辑布局对象
        :param current_user: 当前用户对象
        :param db: orm对象
        :param data_scope_sql: 数据权限对应的查询sql语句
        :return: 编辑布局的layout_id
        """
        existing_layout = await ConferenceRoomLayoutDao.get_layout_by_id(db, edit_layout.layout_id)
        if not existing_layout:
            raise ServiceException(message='布局不存在')

        edit_layout.update_by = current_user.user.user_name
        edit_layout.update_time = datetime.now()

        edit_dict = edit_layout.model_dump(exclude_unset=True)
        edit_dict['layout_id'] = edit_layout.layout_id

        try:
            await ConferenceRoomLayoutDao.edit_layout_dao(db, edit_dict)
            await db.commit()
            return edit_layout.layout_id
        except Exception as e:
            await db.rollback()
            raise e

    @classmethod
    async def delete_layout_services(
        cls,
        delete_layout: DeleteConferenceRoomLayoutModel,
        current_user: CurrentUserModel,
        db: AsyncSession,
        data_scope_sql: ColumnElement,
    ) -> int:
        """
        删除布局信息service

        :param delete_layout: 删除布局对象
        :param current_user: 当前用户对象
        :param db: orm对象
        :param data_scope_sql: 数据权限对应的查询sql语句
        :return: 删除布局的数量
        """
        delete_layout_ids = delete_layout.layout_ids.split(',')
        delete_count = 0

        for layout_id in delete_layout_ids:
            layout_id_int = int(layout_id.strip())
            existing_layout = await ConferenceRoomLayoutDao.get_layout_by_id(db, layout_id_int)
            if existing_layout:
                await ConferenceRoomLayoutDao.delete_layout_dao(db, layout_id_int)
                delete_count += 1

        try:
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise e

        return delete_count

    @classmethod
    async def get_layout_detail_services(
        cls,
        layout_id: int,
        current_user: CurrentUserModel,
        db: AsyncSession,
        data_scope_sql: ColumnElement,
    ) -> dict[str, Any]:
        """
        获取布局详细信息service

        :param layout_id: 布局ID
        :param current_user: 当前用户对象
        :param db: orm对象
        :param data_scope_sql: 数据权限对应的查询sql语句
        :return: 布局详细信息
        """
        existing_layout = await ConferenceRoomLayoutDao.get_layout_by_id(db, layout_id)
        if not existing_layout:
            raise ServiceException(message='布局不存在')

        layout_data = SqlalchemyUtil.serialize_result(existing_layout)

        return layout_data