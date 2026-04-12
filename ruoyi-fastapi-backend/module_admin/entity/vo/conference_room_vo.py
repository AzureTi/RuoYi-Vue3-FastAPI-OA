from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from pydantic.alias_generators import to_camel


class ConferenceRoomModel(BaseModel):
    """
    会议室表对应pydantic模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    room_id: int | None = Field(default=None, description='会议室ID')
    room_name: str | None = Field(default=None, description='会议室名称')
    capacity: int | None = Field(default=None, description='容纳人数')
    location: str | None = Field(default=None, description='位置')
    equipment: str | None = Field(default=None, description='设备配置')
    dept_id: int | None = Field(default=None, description='所属部门ID')
    admin_id: int | None = Field(default=None, description='管理员ID')
    tags: str | None = Field(default=None, description='标签')
    status: Literal['0', '1'] | None = Field(default=None, description='状态（0正常 1停用）')
    del_flag: Literal['0', '2'] | None = Field(default=None, description='删除标志（0代表存在 2代表删除）')
    create_by: str | None = Field(default=None, description='创建者')
    create_time: datetime | None = Field(default=None, description='创建时间')
    update_by: str | None = Field(default=None, description='更新者')
    update_time: datetime | None = Field(default=None, description='更新时间')
    remark: str | None = Field(default=None, description='备注')


class ConferenceRoomQueryModel(ConferenceRoomModel):
    """
    会议室管理不分页查询模型
    """

    begin_time: str | None = Field(default=None, description='开始时间')
    end_time: str | None = Field(default=None, description='结束时间')


class ConferenceRoomPageQueryModel(ConferenceRoomQueryModel):
    """
    会议室管理分页查询模型
    """

    page_num: int = Field(default=1, description='当前页码')
    page_size: int = Field(default=10, description='每页记录数')


class AddConferenceRoomModel(ConferenceRoomModel):
    """
    新增会议室模型
    """


class EditConferenceRoomModel(AddConferenceRoomModel):
    """
    编辑会议室模型
    """


class DeleteConferenceRoomModel(BaseModel):
    """
    删除会议室模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    room_ids: str = Field(description='需要删除的会议室ID')
    update_by: str | None = Field(default=None, description='更新者')
    update_time: datetime | None = Field(default=None, description='更新时间')


class ConferenceRoomLayoutModel(BaseModel):
    """
    会议室布局表对应pydantic模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    layout_id: int | None = Field(default=None, description='布局ID')
    room_id: int | None = Field(default=None, description='会议室ID')
    config: str | None = Field(default=None, description='布局配置')
    seats: str | None = Field(default=None, description='座位信息')
    create_by: str | None = Field(default=None, description='创建者')
    create_time: datetime | None = Field(default=None, description='创建时间')
    update_by: str | None = Field(default=None, description='更新者')
    update_time: datetime | None = Field(default=None, description='更新时间')
    remark: str | None = Field(default=None, description='备注')


class ConferenceRoomLayoutQueryModel(ConferenceRoomLayoutModel):
    """
    会议室布局不分页查询模型
    """


class AddConferenceRoomLayoutModel(ConferenceRoomLayoutModel):
    """
    新增会议室布局模型
    """


class EditConferenceRoomLayoutModel(AddConferenceRoomLayoutModel):
    """
    编辑会议室布局模型
    """


class DeleteConferenceRoomLayoutModel(BaseModel):
    """
    删除会议室布局模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    layout_ids: str = Field(description='需要删除的布局ID')
    update_by: str | None = Field(default=None, description='更新者')
    update_time: datetime | None = Field(default=None, description='更新时间')


class ConferenceRoomDetailModel(BaseModel):
    """
    会议室详情响应模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    data: ConferenceRoomModel | None = Field(default=None, description='会议室信息')
    layouts: list[ConferenceRoomLayoutModel | None] = Field(default=[], description='布局列表')