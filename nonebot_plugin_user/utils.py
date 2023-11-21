import asyncio
import sys
from typing import Optional

from nonebot_plugin_orm import get_session
from sqlalchemy import exc, select

from .models import Bind, User

_insert_mutex: Optional[asyncio.Lock] = None


def _get_insert_mutex():
    # py3.10 以下，Lock 必须在 event_loop 内创建
    global _insert_mutex

    if _insert_mutex is None:
        _insert_mutex = asyncio.Lock()
    elif sys.version_info < (3, 10):
        # 还需要判断 loop 是否与之前创建的一致
        # 单测中不同的 test，loop 也不一样
        # 但是 nonebot 里 loop 始终是一样的
        if getattr(_insert_mutex, "_loop") != asyncio.get_running_loop():
            _insert_mutex = asyncio.Lock()

    return _insert_mutex


async def get_user(platform: str, platform_id: str) -> User:
    """创建账号"""
    async with get_session() as session:
        user = (
            await session.scalars(
                select(User)
                .where(Bind.platform_id == platform_id)
                .where(Bind.platform == platform)
                .join(Bind, User.id == Bind.bind_id)
            )
        ).one_or_none()

        if user:
            return user

    async with _get_insert_mutex():
        try:
            async with get_session(expire_on_commit=False) as session:
                user = User(name=f"{platform}-{platform_id}")
                session.add(user)
                await session.commit()

                bind = Bind(
                    platform_id=platform_id,
                    platform=platform,
                    bind_id=user.id,
                    original_id=user.id,
                )
                session.add(bind)
                await session.commit()
                return user
        except exc.IntegrityError:
            async with get_session() as session:
                user = (
                    await session.scalars(
                        select(User)
                        .where(Bind.platform == platform)
                        .where(Bind.platform_id == platform_id)
                        .join(Bind, User.id == Bind.bind_id)
                    )
                ).one_or_none()

                if not user:
                    raise ValueError("创建用户失败")  # pragma: no cover

                return user


async def get_user_by_id(user_id: int) -> User:
    """通过 user_id 获取账号"""
    async with get_session() as session:
        user = (
            await session.scalars(select(User).where(User.id == user_id))
        ).one_or_none()

        if not user:
            raise ValueError("找不到用户信息")

        return user


async def set_bind(platform: str, platform_id: str, aid: int) -> None:
    """设置账号绑定"""
    async with get_session() as session:
        bind = (
            await session.scalars(
                select(Bind)
                .where(Bind.platform == platform)
                .where(Bind.platform_id == platform_id)
            )
        ).one_or_none()

        if not bind:
            raise ValueError("找不到用户信息")

        bind.bind_id = aid
        await session.commit()


async def set_user_name(platform: str, platform_id: str, name: str) -> None:
    """设置用户名"""
    async with get_session() as session:
        user = (
            await session.scalars(
                select(User)
                .where(Bind.platform == platform)
                .where(Bind.platform_id == platform_id)
                .join(Bind, User.id == Bind.bind_id)
            )
        ).one_or_none()

        if not user:
            raise ValueError("找不到用户信息")

        user.name = name
        await session.commit()


async def remove_bind(platform: str, platform_id: str) -> bool:
    """解除账号绑定"""
    async with get_session() as db_session:
        bind = (
            await db_session.scalars(
                select(Bind)
                .where(Bind.platform == platform)
                .where(Bind.platform_id == platform_id)
            )
        ).one_or_none()

        if not bind:
            raise ValueError("找不到用户信息")

        if bind.bind_id == bind.original_id:
            return False
        else:
            bind.bind_id = bind.original_id
            await db_session.commit()
            return True
