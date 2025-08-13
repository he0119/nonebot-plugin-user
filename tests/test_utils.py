# ruff: noqa: E501
from nonebug import App


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
