from datetime import datetime

from sqlalchemy import CHAR, BigInteger, Column, DateTime, Integer, String

from config.database import Base
from config.env import DataBaseConfig
from utils.common_util import SqlalchemyUtil


class SysMeeting(Base):
    """
    会议信息表
    """

    __tablename__ = 'sys_meeting'
    __table_args__ = {'comment': '会议信息表'}

    meeting_id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment='会议ID')
    meeting_name = Column(String(100), nullable=False, comment='会议名称')
    dept_id = Column(
        BigInteger,
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type, False),
        comment='组织部门ID',
    )
    main_room_id = Column(
        BigInteger,
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type, False),
        comment='主会场会议室ID',
    )
    sub_rooms = Column(
        String(500),
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type),
        comment='分会场会议室ID列表（逗号分隔）',
    )
    start_time = Column(DateTime, nullable=False, comment='会议开始时间')
    duration = Column(Integer, nullable=False, comment='会议时长（分钟）')
    status = Column(CHAR(1), nullable=True, server_default='0', comment='会议状态（0草稿 1待审核 2已通过 3进行中 4已结束）')
    organizer_id = Column(
        BigInteger,
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type, False),
        comment='组织者ID',
    )
    del_flag = Column(CHAR(1), nullable=True, server_default='0', comment='删除标志（0代表存在 2代表删除）')
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
