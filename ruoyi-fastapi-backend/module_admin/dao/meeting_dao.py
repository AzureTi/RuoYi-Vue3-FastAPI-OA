from datetime import datetime, time
from typing import Any

from sqlalchemy import ColumnElement, delete, desc, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from common.vo import PageModel
from module_admin.entity.do.meeting_do import SysMeeting
from module_admin.entity.vo.meeting_vo import MeetingPageQueryModel
from utils.page_util import PageUtil


class MeetingDao:
    """
    会议管理模块数据库操作层
    """

    @classmethod
    async def get_meeting_by_id(cls, db: AsyncSession, meeting_id: int) -> SysMeeting | None:
        """
        根据会议ID获取会议信息

        :param db: orm对象
        :param meeting_id: 会议ID
        :return: 会议信息对象
        """
        query_meeting_info = (
            (
                await db.execute(
                    select(SysMeeting)
                    .where(SysMeeting.del_flag == '0', SysMeeting.meeting_id == meeting_id)
                    .distinct()
                )
            )
            .scalars()
            .first()
        )

        return query_meeting_info

    @classmethod
    async def get_meeting_list(
        cls,
        db: AsyncSession,
        query_object: MeetingPageQueryModel,
        data_scope_sql: ColumnElement,
        is_page: bool = False,
    ) -> PageModel | list[dict[str, Any]]:
        """
        根据查询参数获取会议列表信息

        :param db: orm对象
        :param query_object: 查询参数对象
        :param data_scope_sql: 数据权限对应的查询sql语句
        :param is_page: 是否开启分页
        :return: 会议列表信息对象
        """
        query = (
            select(SysMeeting)
            .where(
                SysMeeting.del_flag == '0',
                SysMeeting.meeting_id == query_object.meeting_id if query_object.meeting_id is not None else True,
                SysMeeting.meeting_name.like(f'%{query_object.meeting_name}%') if query_object.meeting_name else True,
                SysMeeting.status == query_object.status if query_object.status else True,
                SysMeeting.organizer_id == query_object.organizer_id if query_object.organizer_id is not None else True,
                SysMeeting.create_time.between(
                    datetime.combine(datetime.strptime(query_object.begin_time, '%Y-%m-%d'), time(00, 00, 00)),
                    datetime.combine(datetime.strptime(query_object.end_time, '%Y-%m-%d'), time(23, 59, 59)),
                )
                if query_object.begin_time and query_object.end_time
                else True,
                data_scope_sql,
            )
            .order_by(desc(SysMeeting.create_time))
            .distinct()
        )
        meeting_list: PageModel | list[dict[str, Any]] = await PageUtil.paginate(
            db, query, query_object.page_num, query_object.page_size, is_page
        )

        return meeting_list

    @classmethod
    async def add_meeting_dao(cls, db: AsyncSession, meeting: SysMeeting) -> SysMeeting:
        """
        新增会议数据库操作

        :param db: orm对象
        :param meeting: 会议对象
        :return: 新增的会议对象
        """
        db.add(meeting)
        await db.flush()
        await db.refresh(meeting)

        return meeting

    @classmethod
    async def edit_meeting_dao(cls, db: AsyncSession, meeting: dict) -> None:
        """
        编辑会议数据库操作

        :param db: orm对象
        :param meeting: 需要更新的会议字典
        :return: 无返回值
        """
        await db.execute(update(SysMeeting), [meeting])

    @classmethod
    async def delete_meeting_dao(cls, db: AsyncSession, meeting_id: int) -> None:
        """
        删除会议数据库操作

        :param db: orm对象
        :param meeting_id: 会议ID
        :return: 无返回值
        """
        await db.execute(
            update(SysMeeting)
            .where(SysMeeting.meeting_id == meeting_id)
            .values(del_flag='2')
        )

    @classmethod
    async def count_meeting_dao(cls, db: AsyncSession) -> int:
        """
        统计会议数量

        :param db: orm对象
        :return: 会议数量
        """
        count = (
            await db.execute(select(func.count()).select_from(SysMeeting).where(SysMeeting.del_flag == '0'))
        ).scalar()

        return count
