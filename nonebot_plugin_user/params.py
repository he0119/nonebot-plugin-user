from typing import Optional

from nonebot.params import Depends
from nonebot_plugin_uninfo import Session, get_session

from .models import UserSession
from .utils import get_user_depends


async def get_user(session: Optional[Session] = Depends(get_session)):
    """获取一个用户，如果不存在则创建"""

    # session 为 None，说明 session 没有适配此事件
    # 直接返回空用户
    if not session:
        return  # pragma: no cover

    user = await get_user_depends(session.scope, session.user.id)

    return user


async def get_user_session(session: Optional[Session] = Depends(get_session)):
    """获取用户会话"""
    user = await get_user(session)
    if session and user:
        return UserSession(session=session, user=user)
