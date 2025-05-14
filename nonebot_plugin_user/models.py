from datetime import datetime, timezone
from typing_extensions import deprecated

from nonebot.compat import PYDANTIC_V2, ConfigDict
from nonebot_plugin_orm import Model
from nonebot_plugin_uninfo import Session, SceneType
from nonebot_plugin_uninfo import User as UninfoUser
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
    """平台用户 ID"""
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

        # 数据库中使用 UTC 保存时间
        return self.user.created_at.replace(tzinfo=timezone.utc)

    @property
    def adapter(self) -> str:
        """适配器名称"""
        return self.session.adapter

    @property
    def platform(self) -> str:
        """平台名称"""
        return str(self.session.scope)

    scope = platform

    @property
    @deprecated("`UserSession.platform_id` is deprecated, use `UserSession.platform_user.id` instead")
    def platform_id(self) -> str:  # pragma: no cover
        """用户所在平台 ID"""
        return self.session.user.id

    @property
    def platform_user(self) -> UninfoUser:
        """用户于所在平台的实际信息"""
        return self.session.user

    @property
    def type(self) -> SceneType:
        return self.session.scene.type

    @property
    @deprecated("`UserSession.level` is deprecated, use `UserSession.type` instead")
    def level(self):  # pragma: no cover
        """用户会话级别"""
        if self.session.scene.is_private:
            return 1
        elif self.session.scene.is_group:
            return 2
        elif self.session.scene.is_channel or self.session.scene.is_guild:
            return 3
        return 0

    @property
    def session_id(self) -> str:
        """用户会话 ID

        ID 由平台名称和会话场景 ID 组成，例如 `QQClient_123456789`。
        """
        return f"{self.session.scope}_{self.session.scene_path}"

    @property
    @deprecated("`UserSession.group_session_id` is deprecated, use `UserSession.session_id` instead")
    def group_session_id(self) -> str:  # pragma: no cover
        """用户所在群组会话 ID

        ID 由平台名称和平台的群组 ID 组成，例如 `QQClient_123456789`。
        """
        if self.session.group:
            return self.session_id
        return ""
