from typing import List, Optional

from nonebot.adapters import Bot, Event
from nonebot.params import Depends

from nonebot_plugin_user.consts import SessionLevel

from . import utils
from .adapters import MAPPING
from .models import Session, Subject, UserSession


async def extract_session(bot: Bot, event: Event) -> Optional[Session]:
    adapter_name = bot.adapter.get_name()

    if fn := MAPPING.get(adapter_name):
        return fn.get_session(bot, event)


async def extract_subjects(bot: Bot, event: Event) -> List[Subject]:
    adapter_name = bot.adapter.get_name()

    if fn := MAPPING.get(adapter_name):
        return fn.get_subjects(bot, event)

    return []


async def get_or_create_user(session: Session = Depends(extract_session)):
    """获取一个用户，如果不存在则创建"""
    if (
        session.platform == "unknown"
        or session.level == SessionLevel.LEVEL0
        or not session.id1
    ):
        raise ValueError("用户相关功能暂不支持当前平台")

    user = await utils.get_or_create_user(
        session.id1,
        session.platform,
        f"{session.platform}-{session.id1}",
    )

    return user


async def get_user_session(
    session: Session = Depends(extract_session),
    subjects: List[Subject] = Depends(extract_subjects),
) -> UserSession:
    """获取用户会话"""
    user = await get_or_create_user(session)
    return UserSession(session, user, subjects)
