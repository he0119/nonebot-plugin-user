from nonebot.matcher import Matcher
from nonebot.params import Depends
from nonebot_plugin_session import Session, SessionLevel, extract_session

from . import utils
from .models import UserSession


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


async def get_user(
    matcher: Matcher,
    session: Session = Depends(extract_session),
):
    """获取一个用户"""
    try:
        user = await get_or_create_user(session)
    except ValueError as e:  # pragma: no cover
        await matcher.finish(str(e))
    return user


async def get_user_session(
    matcher: Matcher,
    session: Session = Depends(extract_session),
):
    """获取用户会话"""
    user = await get_user(matcher, session)
    return UserSession(session, user)
