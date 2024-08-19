from nonebot.params import Depends
from nonebot_plugin_orm import get_scoped_session
from nonebot_plugin_session import Session, SessionLevel, extract_session
from sqlalchemy.ext.asyncio import async_scoped_session

from .models import UserSession
from .utils import get_user_depends


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

    user = await get_user_depends(session.platform, session.id1)

    return user


async def get_user_session(
    session: Session = Depends(extract_session),
    orm_session: async_scoped_session = Depends(get_scoped_session),
):
    """获取用户会话"""
    user = await get_user(session)
    if user:
        return UserSession(session=session, user=user)
