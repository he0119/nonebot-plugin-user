from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from nonebot_plugin_orm import Model
from nonebot_plugin_session import Session, SessionIdType, SessionLevel
from nonebot_plugin_userinfo import UserInfo
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class User(Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    binds: Mapped[List["Bind"]] = relationship(
        back_populates="bind_user", foreign_keys="[Bind.bind_id]"
    )
    """当前绑定的平台"""
    bind: Mapped["Bind"] = relationship(
        back_populates="original_user", foreign_keys="[Bind.original_id]"
    )
    """初始时绑定的平台"""


class Bind(Model):
    platform: Mapped[str] = mapped_column(String(32), primary_key=True)
    """平台名称"""
    platform_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    """平台 ID"""
    bind_id: Mapped[int] = mapped_column(ForeignKey("nonebot_plugin_user_user.id"))
    """当前绑定的账号 ID"""
    original_id: Mapped[int] = mapped_column(ForeignKey("nonebot_plugin_user_user.id"))
    """初始时绑定的账号 ID"""

    bind_user: Mapped[User] = relationship(
        back_populates="binds", foreign_keys=[bind_id]
    )
    """当前绑定的账号"""
    original_user: Mapped[User] = relationship(
        back_populates="bind", foreign_keys=[original_id]
    )
    """初始时绑定的账号"""


@dataclass
class UserSession:
    session: Session
    info: Optional[UserInfo]
    user: User

    @property
    def user_id(self) -> int:
        """用户 ID"""
        return self.user.id

    @property
    def user_name(self) -> str:
        """用户名"""
        return self.user.name

    @property
    def created_at(self) -> datetime:
        """用户创建日期"""
        return self.user.created_at.astimezone()

    @property
    def platform_id(self) -> str:
        """用户所在平台 ID"""
        assert self.session.id1
        return self.session.id1

    @property
    def platform(self) -> str:
        """用户所在平台"""
        return self.session.platform

    @property
    def level(self) -> SessionLevel:
        """用户会话级别"""
        return self.session.level

    @property
    def group_session_id(self) -> str:
        """用户所在群组会话 ID

        ID 由平台名称和平台的群组 ID 组成，例如 `qq_123456789`。
        """
        return self.session.get_id(
            id_type=SessionIdType.GROUP,
            include_platform=True,
            include_bot_type=False,
            include_bot_id=False,
        )
