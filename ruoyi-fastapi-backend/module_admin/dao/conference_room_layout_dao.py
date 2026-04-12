import json
from typing import Any, Optional

from sqlalchemy import ColumnElement, delete, desc, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from common.vo import PageModel
from module_admin.entity.do.conference_room_layout_do import SysConferenceRoomLayout
from module_admin.entity.vo.conference_room_vo import (
    ConferenceRoomLayoutModel,
    ConferenceRoomLayoutQueryModel,
)
from utils.page_util import PageUtil


class ConferenceRoomLayoutDao:
    """
    会议室布局管理模块数据库操作层
    """

    @classmethod
    async def get_conference_room_layout_by_room_id_dao(
        cls,
        db: AsyncSession,
        room_id: int
    ) -> Optional[SysConferenceRoomLayout]:
        """
        根据会议室ID获取布局信息

        :param db: 数据库会话
        :param room_id: 会议室ID
        :return: 布局信息
        """
        query = select(SysConferenceRoomLayout).where(
            SysConferenceRoomLayout.room_id == room_id
        )
        result = await db.execute(query)
        return result.scalars().first()

    @classmethod
    async def get_layout_by_id(cls, db: AsyncSession, layout_id: int) -> SysConferenceRoomLayout | None:
        """
        根据布局ID获取布局信息

        :param db: orm对象
        :param layout_id: 布局ID
        :return: 布局信息对象
        """
        query_layout_info = (
            (
                await db.execute(
                    select(SysConferenceRoomLayout)
                    .where(SysConferenceRoomLayout.layout_id == layout_id)
                    .distinct()
                )
            )
            .scalars()
            .first()
        )

        return query_layout_info

    @classmethod
    async def get_layout_list_by_room_id(cls, db: AsyncSession, room_id: int) -> list[SysConferenceRoomLayout]:
        """
        根据会议室ID获取布局列表

        :param db: orm对象
        :param room_id: 会议室ID
        :return: 布局列表
        """
        query_layout_list = (
            (
                await db.execute(
                    select(SysConferenceRoomLayout)
                    .where(SysConferenceRoomLayout.room_id == room_id)
                    .order_by(desc(SysConferenceRoomLayout.create_time))
                    .distinct()
                )
            )
            .scalars()
            .all()
        )

        return query_layout_list

    @classmethod
    async def get_layout_list(
        cls,
        db: AsyncSession,
        query_object: ConferenceRoomLayoutQueryModel,
        data_scope_sql: ColumnElement,
        is_page: bool = False,
        page_num: int = 1,
        page_size: int = 10,
    ) -> PageModel | list[dict[str, Any]]:
        """
        根据查询参数获取布局列表信息

        :param db: orm对象
        :param query_object: 查询参数对象
        :param data_scope_sql: 数据权限对应的查询sql语句
        :param is_page: 是否开启分页
        :param page_num: 当前页码
        :param page_size: 每页记录数
        :return: 布局列表信息对象
        """
        query = (
            select(SysConferenceRoomLayout)
            .where(
                SysConferenceRoomLayout.layout_id == query_object.layout_id
                if query_object.layout_id is not None
                else True,
                SysConferenceRoomLayout.room_id == query_object.room_id
                if query_object.room_id is not None
                else True,
                data_scope_sql,
            )
            .order_by(desc(SysConferenceRoomLayout.create_time))
            .distinct()
        )
        layout_list: PageModel | list[dict[str, Any]] = await PageUtil.paginate(
            db, query, page_num, page_size, is_page
        )

        return layout_list

    @classmethod
    async def add_conference_room_layout_dao(
        cls,
        db: AsyncSession,
        layout: SysConferenceRoomLayout
    ) -> SysConferenceRoomLayout:
        """
        添加会议室布局

        :param db: 数据库会话
        :param layout: 布局信息
        :return: 布局信息
        """
        db.add(layout)
        await db.flush()
        await db.refresh(layout)
        return layout

    @classmethod
    async def add_layout_dao(cls, db: AsyncSession, layout: ConferenceRoomLayoutModel) -> SysConferenceRoomLayout:
        """
        新增布局数据库操作

        :param db: orm对象
        :param layout: 布局对象
        :return: 新增的布局对象
        """
        db_layout = SysConferenceRoomLayout(**layout.model_dump(by_alias=False))
        db.add(db_layout)
        await db.flush()
        await db.refresh(db_layout)

        return db_layout

    @classmethod
    async def update_conference_room_layout_dao(
        cls,
        db: AsyncSession,
        room_id: int,
        layout_data: dict
    ) -> Optional[SysConferenceRoomLayout]:
        """
        更新会议室布局

        :param db: 数据库会话
        :param room_id: 会议室ID
        :param layout_data: 布局数据
        :return: 布局信息
        """
        layout = await cls.get_conference_room_layout_by_room_id_dao(db, room_id)
        if not layout:
            return None

        query = update(SysConferenceRoomLayout).where(
            SysConferenceRoomLayout.room_id == room_id
        ).values(**layout_data)
        await db.execute(query)
        await db.flush()
        layout = await cls.get_conference_room_layout_by_room_id_dao(db, room_id)
        return layout

    @classmethod
    async def edit_layout_dao(cls, db: AsyncSession, layout: dict) -> None:
        """
        编辑布局数据库操作

        :param db: orm对象
        :param layout: 需要更新的布局字典
        :return: 无返回值
        """
        await db.execute(update(SysConferenceRoomLayout), [layout])

    @classmethod
    async def delete_conference_room_layout_dao(
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
        query = delete(SysConferenceRoomLayout).where(
            SysConferenceRoomLayout.room_id == room_id
        )
        result = await db.execute(query)
        return result.rowcount > 0

    @classmethod
    async def delete_layout_dao(cls, db: AsyncSession, layout_id: int) -> None:
        """
        删除布局数据库操作

        :param db: orm对象
        :param layout_id: 布局ID
        :return: 无返回值
        """
        await db.execute(delete(SysConferenceRoomLayout).where(SysConferenceRoomLayout.layout_id == layout_id))

    @classmethod
    async def delete_layout_by_room_id_dao(cls, db: AsyncSession, room_id: int) -> None:
        """
        根据会议室ID删除布局数据库操作

        :param db: orm对象
        :param room_id: 会议室ID
        :return: 无返回值
        """
        await db.execute(delete(SysConferenceRoomLayout).where(SysConferenceRoomLayout.room_id == room_id))