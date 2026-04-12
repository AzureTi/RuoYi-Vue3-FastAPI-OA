from datetime import datetime

from sqlalchemy import CHAR, BigInteger, Column, DateTime, Integer, String, Text

from config.database import Base
from config.env import DataBaseConfig
from utils.common_util import SqlalchemyUtil


class SysConferenceRoom(Base):
    """
    会议室信息表
    """

    __tablename__ = 'sys_conference_room'
    __table_args__ = {'comment': '会议室信息表'}

    room_id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment='会议室ID')
    room_name = Column(String(50), nullable=False, comment='会议室名称')
    capacity = Column(Integer, nullable=False, comment='容纳人数')
    location = Column(String(100), nullable=False, comment='位置')
    equipment = Column(String(200), nullable=True, server_default="''", comment='设备配置')
    dept_id = Column(
        BigInteger,
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type, False),
        comment='所属部门ID',
    )
    admin_id = Column(
        BigInteger,
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type, False),
        comment='管理员ID',
    )
    tags = Column(String(200), nullable=True, server_default="''", comment='标签')
    status = Column(CHAR(1), nullable=True, server_default='0', comment='状态（0正常 1停用）')
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