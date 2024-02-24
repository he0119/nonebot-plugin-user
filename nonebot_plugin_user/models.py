from datetime import datetime

from nonebot.compat import PYDANTIC_V2, ConfigDict
from nonebot_plugin_orm import Model
from nonebot_plugin_session import Session, SessionIdType, SessionLevel
from pydantic import BaseModel
from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column


class User(Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Bind(Model):
    platform: Mapped[str] = mapped_column(String(32), primary_key=True)
    """平台名称"""
    platform_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    """平台 ID"""
    bind_id: Mapped[int]
    """当前绑定的账号 ID"""
    original_id: Mapped[int]
    """初始时绑定的账号 ID"""


class UserSession(BaseModel):
    if PYDANTIC_V2:
        model_config = ConfigDict(arbitrary_types_allowed=True)
    else:

        class Config:  # pragma: no cover
            arbitrary_types_allowed = True

    session: Session
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
