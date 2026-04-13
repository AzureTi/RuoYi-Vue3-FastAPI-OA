from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from pydantic.alias_generators import to_camel


class MeetingModel(BaseModel):
    """
    会议表对应pydantic模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    meeting_id: int | None = Field(default=None, description='会议ID')
    meeting_name: str | None = Field(default=None, description='会议名称')
    dept_id: int | None = Field(default=None, description='组织部门ID')
    main_room_id: int | None = Field(default=None, description='主会场会议室ID')
    sub_rooms: str | None = Field(default=None, description='分会场会议室ID列表（逗号分隔）')
    start_time: datetime | None = Field(default=None, description='会议开始时间')
    duration: int | None = Field(default=None, description='会议时长（分钟）')
    status: Literal['0', '1', '2', '3', '4'] | None = Field(default=None, description='会议状态（0草稿 1待审核 2已通过 3进行中 4已结束）')
    organizer_id: int | None = Field(default=None, description='组织者ID')
    del_flag: Literal['0', '2'] | None = Field(default=None, description='删除标志（0代表存在 2代表删除）')
    create_by: str | None = Field(default=None, description='创建者')
    create_time: datetime | None = Field(default=None, description='创建时间')
    update_by: str | None = Field(default=None, description='更新者')
    update_time: datetime | None = Field(default=None, description='更新时间')
    remark: str | None = Field(default=None, description='备注')


class MeetingQueryModel(MeetingModel):
    """
    会议管理不分页查询模型
    """

    begin_time: str | None = Field(default=None, description='开始时间')
    end_time: str | None = Field(default=None, description='结束时间')


class MeetingPageQueryModel(MeetingQueryModel):
    """
    会议管理分页查询模型
    """

    page_num: int = Field(default=1, description='当前页码')
    page_size: int = Field(default=10, description='每页记录数')


class AddMeetingModel(MeetingModel):
    """
    新增会议模型
    """


class EditMeetingModel(AddMeetingModel):
    """
    编辑会议模型
    """


class DeleteMeetingModel(BaseModel):
    """
    删除会议模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    meeting_ids: str = Field(description='需要删除的会议ID')
    update_by: str | None = Field(default=None, description='更新者')
    update_time: datetime | None = Field(default=None, description='更新时间')


class MeetingDetailModel(BaseModel):
    """
    会议详情响应模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    data: MeetingModel | None = Field(default=None, description='会议信息')
    main_room_name: str | None = Field(default=None, description='主会场名称')
    sub_room_names: list[str] = Field(default=[], description='分会场名称列表')
