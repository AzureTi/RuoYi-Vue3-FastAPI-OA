from datetime import datetime, time
from typing import Any

from sqlalchemy import ColumnElement, and_, delete, desc, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from common.vo import PageModel
from module_admin.entity.do.conference_room_do import SysConferenceRoom
from module_admin.entity.vo.conference_room_vo import (
    ConferenceRoomModel,
    ConferenceRoomPageQueryModel,
)
from utils.page_util import PageUtil


class ConferenceRoomDao:
    """
    会议室管理模块数据库操作层
    """

    @classmethod
    async def get_conference_room_by_id(cls, db: AsyncSession, room_id: int) -> SysConferenceRoom | None:
        """
        根据会议室ID获取会议室信息

        :param db: orm对象
        :param room_id: 会议室ID
        :return: 会议室信息对象
        """
        query_room_info = (
            (
                await db.execute(
                    select(SysConferenceRoom)
                    .where(SysConferenceRoom.del_flag == '0', SysConferenceRoom.room_id == room_id)
                    .distinct()
                )
            )
            .scalars()
            .first()
        )

        return query_room_info

    @classmethod
    async def get_conference_room_by_id_without_scope(cls, db: AsyncSession, room_id: int) -> SysConferenceRoom | None:
        """
        根据会议室ID获取会议室信息（不带数据权限）

        :param db: orm对象
        :param room_id: 会议室ID
        :return: 会议室信息对象
        """
        query_room_info = (
            (
                await db.execute(
                    select(SysConferenceRoom)
                    .where(SysConferenceRoom.room_id == room_id)
                    .distinct()
                )
            )
            .scalars()
            .first()
        )

        return query_room_info

    @classmethod
    async def get_conference_room_by_name(cls, db: AsyncSession, room_name: str) -> SysConferenceRoom | None:
        """
        根据会议室名称获取会议室信息

        :param db: orm对象
        :param room_name: 会议室名称
        :return: 会议室信息对象
        """
        query_room_info = (
            (
                await db.execute(
                    select(SysConferenceRoom)
                    .where(SysConferenceRoom.del_flag == '0', SysConferenceRoom.room_name == room_name)
                    .distinct()
                )
            )
            .scalars()
            .first()
        )

        return query_room_info

    @classmethod
    async def get_conference_room_list(
        cls,
        db: AsyncSession,
        query_object: ConferenceRoomPageQueryModel,
        data_scope_sql: ColumnElement,
        is_page: bool = False,
    ) -> PageModel | list[dict[str, Any]]:
        """
        根据查询参数获取会议室列表信息

        :param db: orm对象
        :param query_object: 查询参数对象
        :param data_scope_sql: 数据权限对应的查询sql语句
        :param is_page: 是否开启分页
        :return: 会议室列表信息对象
        """
        query = (
            select(SysConferenceRoom)
            .where(
                SysConferenceRoom.del_flag == '0',
                SysConferenceRoom.room_id == query_object.room_id if query_object.room_id is not None else True,
                SysConferenceRoom.room_name.like(f'%{query_object.room_name}%') if query_object.room_name else True,
                SysConferenceRoom.location.like(f'%{query_object.location}%') if query_object.location else True,
                SysConferenceRoom.dept_id == query_object.dept_id if query_object.dept_id is not None else True,
                SysConferenceRoom.status == query_object.status if query_object.status else True,
                SysConferenceRoom.capacity >= query_object.capacity if query_object.capacity is not None else True,
                SysConferenceRoom.create_time.between(
                    datetime.combine(datetime.strptime(query_object.begin_time, '%Y-%m-%d'), time(00, 00, 00)),
                    datetime.combine(datetime.strptime(query_object.end_time, '%Y-%m-%d'), time(23, 59, 59)),
                )
                if query_object.begin_time and query_object.end_time
                else True,
                data_scope_sql,
            )
            .order_by(desc(SysConferenceRoom.create_time))
            .distinct()
        )
        room_list: PageModel | list[dict[str, Any]] = await PageUtil.paginate(
            db, query, query_object.page_num, query_object.page_size, is_page
        )

        return room_list

    @classmethod
    async def add_conference_room_dao(cls, db: AsyncSession, room: ConferenceRoomModel) -> SysConferenceRoom:
        """
        新增会议室数据库操作

        :param db: orm对象
        :param room: 会议室对象
        :return: 新增的会议室对象
        """
        db_room = SysConferenceRoom(**room.model_dump(by_alias=False))
        db.add(db_room)
        await db.flush()
        await db.refresh(db_room)

        return db_room

    @classmethod
    async def edit_conference_room_dao(cls, db: AsyncSession, room: dict) -> None:
        """
        编辑会议室数据库操作

        :param db: orm对象
        :param room: 需要更新的会议室字典
        :return: 无返回值
        """
        await db.execute(update(SysConferenceRoom), [room])

    @classmethod
    async def delete_conference_room_dao(cls, db: AsyncSession, room: ConferenceRoomModel) -> None:
        """
        删除会议室数据库操作

        :param db: orm对象
        :param room: 会议室对象
        :return: 无返回值
        """
        await db.execute(
            update(SysConferenceRoom)
            .where(SysConferenceRoom.room_id == room.room_id)
            .values(del_flag='2', update_by=room.update_by, update_time=room.update_time)
        )

    @classmethod
    async def count_conference_room_dao(cls, db: AsyncSession) -> int:
        """
        统计会议室数量

        :param db: orm对象
        :return: 会议室数量
        """
        count = (
            await db.execute(select(func.count()).select_from(SysConferenceRoom).where(SysConferenceRoom.del_flag == '0'))
        ).scalar()

        return count