# ruff: noqa: E501
import pytest
from nonebug import App
from pytest_mock import MockerFixture
from sqlalchemy import select


async def test_get_user_platform_id(app: App):
    """测试获取用户在指定平台的 ID 列表"""
    from nonebot_plugin_user.utils import get_user, get_user_platform_ids, set_bind

    user = await get_user("QQClient", "10")
    assert user.id == 1
    assert user.name == "QQClient-10"
    assert await get_user_platform_ids("QQClient", user.id) == ["10"]

    user_10000 = await get_user("QQClient", "10000")
    assert user_10000.id == 2
    assert user_10000.name == "QQClient-10000"
    assert await get_user_platform_ids("QQClient", user.id) == ["10"]
    assert await get_user_platform_ids("QQClient", user_10000.id) == ["10000"]

    # 设置绑定
    await set_bind("QQClient", "10000", user.id)

    assert await get_user_platform_ids("QQClient", user.id) == ["10", "10000"]
    assert await get_user_platform_ids("QQClient", user_10000.id) == []


async def test_set_user_profile(app: App):
    """测试直接设置用户名和邮箱"""
    from nonebot_plugin_orm import get_session

    from nonebot_plugin_user.models import User
    from nonebot_plugin_user.utils import get_user, set_user_email, set_user_name

    user = await get_user("QQClient", "10")

    await set_user_name("QQClient", "10", "new-name")
    await set_user_email("QQClient", "10", "new@example.com")

    async with get_session() as session:
        updated_user = (await session.scalars(select(User).where(User.id == user.id))).one()

    assert updated_user.name == "new-name"
    assert updated_user.email == "new@example.com"


async def test_remove_bind_utils(app: App):
    """测试直接解除绑定"""
    from nonebot_plugin_user.utils import get_user, remove_bind, set_bind

    original_user = await get_user("QQClient", "10")

    assert await remove_bind("QQClient", "10") is False

    bound_user = await get_user("QQClient", "20")
    await set_bind("QQClient", "20", original_user.id)

    assert await remove_bind("QQClient", "20") is True
    assert (await get_user("QQClient", "20")).id == bound_user.id

    with pytest.raises(ValueError, match="找不到用户信息"):
        await remove_bind("QQClient", "30")


async def test_create_user_falls_back_after_integrity_error(app: App, mocker: MockerFixture):
    """测试并发插入触发唯一约束后回查已创建用户"""
    from nonebot_plugin_orm import get_session

    from nonebot_plugin_user import utils
    from nonebot_plugin_user.models import Bind, User

    async with get_session(expire_on_commit=False) as session:
        user = User(name="QQClient-race")
        session.add(user)
        await session.flush()
        session.add(
            Bind(
                platform="QQClient",
                platform_id="race",
                bind_id=user.id,
                original_id=user.id,
            )
        )
        await session.commit()
        await session.refresh(user)
        user_id = user.id

    async def miss_existing_user(*args):
        return None

    mocker.patch("nonebot_plugin_user.utils._get_user", miss_existing_user)

    user = await utils._create_user("QQClient", "race")

    assert user.id == user_id
