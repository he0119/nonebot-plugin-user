import asyncio
from collections.abc import Sequence
from typing import Optional, Union

from nonebot_plugin_orm import get_scoped_session, get_session
from nonebot_plugin_uninfo import SupportScope
from sqlalchemy import exc, select

from .models import Bind, User

_insert_mutex: Optional[asyncio.Lock] = None


def _get_insert_mutex():
    global _insert_mutex

    if _insert_mutex is None:  # pragma: no cover
        _insert_mutex = asyncio.Lock()

    return _insert_mutex


async def _get_user(session, platform: str, user_id: str) -> Optional[User]:
    """获取账号"""
    return (
        await session.scalars(
            select(User)
            .where(Bind.platform_id == user_id)
            .where(Bind.platform == platform)
            .join(Bind, User.id == Bind.bind_id)
        )
    ).one_or_none()


async def create_user(platform: Union[str, SupportScope], user_id: str) -> User:
    """创建账号"""
    async with _get_insert_mutex():
        try:
            async with get_session(expire_on_commit=False) as session:
                user = User(name=f"{platform}-{user_id}")
                session.add(user)
                await session.commit()

                bind = Bind(
                    platform_id=user_id,
                    platform=f"{platform}",
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
                        .where(Bind.platform == f"{platform}")
                        .where(Bind.platform_id == user_id)
                        .join(Bind, User.id == Bind.bind_id)
                    )
                ).one_or_none()

                if not user:  # pragma: no cover
                    raise ValueError("创建用户失败")
    return user


async def get_user(platform: Union[str, SupportScope], user_id: str) -> User:
    """获取或创建账号"""
    async with get_session() as session:
        user = await _get_user(session, f"{platform}", user_id)

    if not user:
        user = await create_user(platform, user_id)

    return user


async def get_user_depends(platform: Union[str, SupportScope], user_id: str) -> User:
    """获取或创建账号（依赖注入专用）

    使用 scoped_session 来进行数据库操作
    """
    scoped_session = get_scoped_session()

    user = await _get_user(scoped_session, f"{platform}", user_id)

    if not user:
        user = await create_user(platform, user_id)
        # 当前 user 是在新的 session 中创建的，需要 merge 到 scoped_session 中
        user = await scoped_session.merge(user)

    return user


async def get_user_by_id(uid: int) -> User:
    """通过 user_id 获取账号"""
    async with get_session() as session:
        user = (await session.scalars(select(User).where(User.id == uid))).one_or_none()

        if not user:
            raise ValueError("找不到用户信息")

        return user


async def set_bind(platform: Union[str, SupportScope], user_id: str, aid: int) -> None:
    """设置账号绑定"""
    async with get_session() as session:
        bind = (
            await session.scalars(
                select(Bind).where(Bind.platform == f"{platform}").where(Bind.platform_id == user_id)
            )
        ).one_or_none()

        if not bind:
            raise ValueError("找不到用户信息")
        else:
            bind.bind_id = aid
            await session.commit()


async def set_user_name(platform: Union[str, SupportScope], user_id: str, name: str) -> None:
    """设置用户名"""
    async with get_session() as session:
        user = (
            await session.scalars(
                select(User)
                .where(Bind.platform == f"{platform}")
                .where(Bind.platform_id == user_id)
                .join(Bind, User.id == Bind.bind_id)
            )
        ).one_or_none()

        if not user:
            raise ValueError("找不到用户信息")

        user.name = name
        await session.commit()


async def set_user_email(platform: Union[str, SupportScope], user_id: str, email: Optional[str]) -> None:
    """设置用户邮箱"""
    async with get_session() as session:
        user = (
            await session.scalars(
                select(User)
                .where(Bind.platform == f"{platform}")
                .where(Bind.platform_id == user_id)
                .join(Bind, User.id == Bind.bind_id)
            )
        ).one_or_none()

        if not user:
            raise ValueError("找不到用户信息")

        user.email = email
        await session.commit()


async def remove_bind(platform: Union[str, SupportScope], user_id: str) -> bool:
    """解除账号绑定"""
    async with get_session() as db_session:
        bind = (
            await db_session.scalars(
                select(Bind).where(Bind.platform == f"{platform}").where(Bind.platform_id == user_id)
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


async def get_user_platform_ids(platform: Union[str, SupportScope], uid: int) -> Sequence[str]:
    """获取用户在指定平台的 ID 列表"""
    async with get_session() as session:
        binds = (
            await session.scalars(
                select(Bind.platform_id).where(Bind.bind_id == uid).where(Bind.platform == f"{platform}")
            )
        ).all()

        return binds
