import asyncio
from typing import Optional

from nonebot_plugin_orm import get_scoped_session, get_session
from sqlalchemy import exc, select

from .models import Bind, User

_insert_mutex: Optional[asyncio.Lock] = None


def _get_insert_mutex():
    global _insert_mutex

    if _insert_mutex is None:  # pragma: no cover
        _insert_mutex = asyncio.Lock()

    return _insert_mutex


async def _get_user(session, platform: str, platform_id: str) -> Optional[User]:
    """获取账号"""
    return (
        await session.scalars(
            select(User)
            .where(Bind.platform_id == platform_id)
            .where(Bind.platform == platform)
            .join(Bind, User.id == Bind.bind_id)
        )
    ).one_or_none()


async def create_user(platform: str, platform_id: str) -> User:
    """创建账号"""
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


async def get_user(platform: str, platform_id: str) -> User:
    """获取或创建账号"""
    async with get_session() as session:
        user = await _get_user(session, platform, platform_id)

    if not user:
        user = await create_user(platform, platform_id)

    return user


async def get_user_depends(platform: str, platform_id: str) -> User:
    """获取或创建账号（依赖注入专用）

    使用 scoped_session 来进行数据库操作
    """
    scoped_session = get_scoped_session()

    user = await _get_user(scoped_session, platform, platform_id)

    if not user:
        user = await create_user(platform, platform_id)
        # 当前 user 是在新的 session 中创建的，需要 merge 到 scoped_session 中
        user = await scoped_session.merge(user)

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
