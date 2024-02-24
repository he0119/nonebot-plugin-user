from nonebot.params import Depends
from nonebot_plugin_session import Session, SessionLevel, extract_session

from .models import UserSession
from .utils import get_user as _get_user


async def get_user(session: Session = Depends(extract_session)):
    """获取一个用户，如果不存在则创建"""

    # 如果是未知平台，或者是 LEVEL0 会话，或者没有 id1，说明 session 没有适配此事件
    # 直接返回空用户
    if (
        session.platform == "unknown"
        or session.level == SessionLevel.LEVEL0
        or not session.id1
    ):
        return  # pragma: no cover

    user = await _get_user(session.platform, session.id1)

    return user


async def get_user_session(session: Session = Depends(extract_session)):
    """获取用户会话"""
    user = await get_user(session)
    if user:
        return UserSession(session=session, user=user)
