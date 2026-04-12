from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, String, Text

from config.database import Base
from config.env import DataBaseConfig
from utils.common_util import SqlalchemyUtil


class SysConferenceRoomLayout(Base):
    """
    会议室布局表
    """

    __tablename__ = 'sys_conference_room_layout'
    __table_args__ = {'comment': '会议室布局表'}

    layout_id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment='布局ID')
    room_id = Column(BigInteger, nullable=False, comment='会议室ID')
    config = Column(Text, nullable=True, comment='布局配置')
    seats = Column(Text, nullable=True, comment='座位信息')
    create_by = Column(String(64), nullable=True, server_default="''", comment='创建者')
    create_time = Column(DateTime, nullable=True, comment='创建时间', default=datetime.now())
    update_by = Column(String(64), nullable=True, server_default="''", comment='更新者')
    update_time = Column(DateTime, nullable=True, comment='更新时间', default=datetime.now())
    remark = Column(
        String(500),
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type),
        comment='备注',
    )