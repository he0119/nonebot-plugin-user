from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Union

from nonebot_plugin_orm import Model
from pydantic import BaseModel
from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from .consts import SessionIdType, SessionLevel


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


class Session(BaseModel):
    bot_id: str
    bot_type: str
    platform: str
    level: SessionLevel
    id1: Optional[str] = None
    id2: Optional[str] = None
    id3: Optional[str] = None

    def get_id(
        self,
        id_type: Union[int, SessionIdType],
        *,
        include_platform: bool = True,
        include_bot_type: bool = True,
        include_bot_id: bool = True,
        seperator: str = "_",
    ) -> str:
        id_type = min(max(id_type, 0), SessionIdType.GROUP_USER)

        if self.level == SessionLevel.LEVEL0:
            id_type = 0
        elif self.level == SessionLevel.LEVEL1:
            id_type = int(bool(id_type))
        elif self.level == SessionLevel.LEVEL2:
            id_type = (id_type & 1) | (int(bool(id_type >> 1)) << 1)
        elif self.level == SessionLevel.LEVEL3:
            pass

        include_id1 = bool(id_type & 1)
        include_id2 = bool((id_type >> 1) & 1)
        include_id3 = bool((id_type >> 2) & 1)

        parts: List[str] = []
        if include_platform:
            parts.append(self.platform)
        if include_bot_type:
            parts.append(self.bot_type)
        if include_bot_id:
            parts.append(self.bot_id)
        if include_id3:
            parts.append(self.id3 or "")
        if include_id2:
            parts.append(self.id2 or "")
        if include_id1:
            parts.append(self.id1 or "")

        return seperator.join(parts)


@dataclass
class UserSession:
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
