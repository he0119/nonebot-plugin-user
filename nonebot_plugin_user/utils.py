from nonebot_plugin_orm import get_session
from sqlalchemy import select

from .models import Bind, User


async def create_user(platform_id: str, platform: str, name: str):
    """创建账号"""
    async with get_session(expire_on_commit=False) as session:
        user = User(name=name)
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


async def get_user(platform_id: str, platform: str):
    """获取账号"""
    async with get_session() as session:
        user = (
            await session.scalars(
                select(User)
                .where(Bind.platform_id == platform_id)
                .where(Bind.platform == platform)
                .join(Bind, User.id == Bind.bind_id)
            )
        ).one_or_none()

        if not user:
            raise ValueError("找不到用户信息")

        return user


async def get_user_by_id(user_id: int):
    """通过 user_id 获取账号"""
    async with get_session() as session:
        user = (
            await session.scalars(select(User).where(User.id == user_id))
        ).one_or_none()

        if not user:
            raise ValueError("找不到用户信息")

        return user


async def set_bind(platform_id: str, platform: str, aid: int):
    """设置账号绑定"""
    async with get_session() as session:
        bind = (
            await session.scalars(
                select(Bind)
                .where(Bind.platform_id == platform_id)
                .where(Bind.platform == platform)
            )
        ).one_or_none()

        if not bind:
            raise ValueError("找不到用户信息")

        bind.bind_id = aid
        await session.commit()


async def set_user_name(platform_id: str, platform: str, name: str):
    """设置用户名"""
    async with get_session() as session:
        user = (
            await session.scalars(
                select(User)
                .where(Bind.platform_id == platform_id)
                .where(Bind.platform == platform)
                .join(Bind, User.id == Bind.bind_id)
            )
        ).one_or_none()

        if not user:
            raise ValueError("找不到用户信息")

        user.name = name
        await session.commit()


async def remove_bind(platform_id: str, platform: str):
    """解除账号绑定"""
    async with get_session() as db_session:
        bind = (
            await db_session.scalars(
                select(Bind)
                .where(Bind.platform_id == platform_id)
                .where(Bind.platform == platform)
            )
        ).one()

        if bind.bind_id == bind.original_id:
            return False
        else:
            bind.bind_id = bind.original_id
            await db_session.commit()
            return True


async def get_or_create_user(platform_id: str, platform: str, name: str):
    """获取一个用户，如果不存在则创建"""
    try:
        user = await get_user(platform_id, platform)
    except ValueError:
        user = await create_user(platform_id, platform, name)

    return user
