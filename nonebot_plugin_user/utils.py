import asyncio
from collections.abc import Sequence

from nonebot_plugin_orm import get_scoped_session, get_session
from nonebot_plugin_uninfo import SupportScope
from sqlalchemy import exc, select

from .models import Bind, User

_insert_mutex: asyncio.Lock | None = None
_create_user_tasks: dict[tuple[str, str], asyncio.Task[User]] = {}


def _get_insert_mutex():
    global _insert_mutex

    if _insert_mutex is None:  # pragma: no cover
        _insert_mutex = asyncio.Lock()

    return _insert_mutex


def _remove_create_user_task(key: tuple[str, str], task: asyncio.Task[User]) -> None:
    if _create_user_tasks.get(key) is task:
        _create_user_tasks.pop(key, None)


async def _get_user(session, platform: str, user_id: str) -> User | None:
    """获取账号"""
    return (
        await session.scalars(
            select(User)
            .where(Bind.platform_id == user_id)
            .where(Bind.platform == platform)
            .join(Bind, User.id == Bind.bind_id)
        )
    ).one_or_none()


async def create_user(platform: str | SupportScope, user_id: str) -> User:
    """创建账号，并复用同一平台账号正在进行的创建任务"""
    key = (f"{platform}", user_id)

    task = _create_user_tasks.get(key)
    if task is None:
        task = asyncio.create_task(_create_user(platform, user_id))
        _create_user_tasks[key] = task
        task.add_done_callback(lambda task: _remove_create_user_task(key, task))

    # 同一个平台账号的并发请求会等待同一个创建任务，避免它们逐个进入锁内查库。
    # shield 可以防止某个调用方被取消时连带取消共享任务，影响其他等待者。
    return await asyncio.shield(task)


async def _create_user(platform: str | SupportScope, user_id: str) -> User:
    """创建账号"""
    async with _get_insert_mutex():
        async with get_session(expire_on_commit=False) as session:
            # create_user() 通常会合并同一平台账号的并发创建请求，但这里仍
            # 保留锁内最终确认，覆盖跨任务清理边界和跨进程等数据库层竞态。
            # 如果省略这次检查，后进入的协程可能会继续插入同名 User，
            # 先触发 User.name 唯一约束；此时 Bind 记录可能还不可见，
            # IntegrityError 兜底回查就会找不到用户。
            user = await _get_user(session, f"{platform}", user_id)
            if user:
                return user

            try:
                user = User(name=f"{platform}-{user_id}")
                session.add(user)
                await session.flush()

                bind = Bind(
                    platform_id=user_id,
                    platform=f"{platform}",
                    bind_id=user.id,
                    original_id=user.id,
                )
                session.add(bind)
                await session.commit()
                await session.refresh(user)
            except exc.IntegrityError:
                await session.rollback()
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


async def get_user(platform: str | SupportScope, user_id: str) -> User:
    """获取或创建账号"""
    async with get_session() as session:
        user = await _get_user(session, f"{platform}", user_id)

    if not user:
        user = await create_user(platform, user_id)

    return user


async def get_user_depends(platform: str | SupportScope, user_id: str) -> User:
    """获取或创建账号（依赖注入专用）

    使用 scoped_session 来进行数据库操作
    """
    scoped_session = get_scoped_session()

    user = await _get_user(scoped_session, f"{platform}", user_id)

    if not user:
        user = await create_user(platform, user_id)
        # 当前 user 是在新的 session 中创建并提交的，需要 merge 到 scoped_session 中。
        # create_user() 返回前已经 refresh 过 user，这里只需要把对象附加到
        # scoped_session，不需要再从数据库加载一次状态。
        user = await scoped_session.merge(user, load=False)

    return user


async def get_user_by_id(uid: int) -> User:
    """通过 user_id 获取账号"""
    async with get_session() as session:
        user = (await session.scalars(select(User).where(User.id == uid))).one_or_none()

        if not user:
            raise ValueError("找不到用户信息")

        return user


async def set_bind(platform: str | SupportScope, user_id: str, aid: int) -> None:
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


async def set_user_name(platform: str | SupportScope, user_id: str, name: str) -> None:
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


async def set_user_email(platform: str | SupportScope, user_id: str, email: str | None) -> None:
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


async def remove_bind(platform: str | SupportScope, user_id: str) -> bool:
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


async def get_user_platform_ids(platform: str | SupportScope, uid: int) -> Sequence[str]:
    """获取用户在指定平台的 ID 列表"""
    async with get_session() as session:
        binds = (
            await session.scalars(
                select(Bind.platform_id).where(Bind.bind_id == uid).where(Bind.platform == f"{platform}")
            )
        ).all()

        return binds
