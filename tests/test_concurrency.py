import asyncio
import random

from nonebot import get_adapter
from nonebot.adapters.onebot.v11 import Adapter, Bot, Message
from nonebug import App
from sqlalchemy import select

from tests.fake import fake_group_message_event_v11


async def test_concurrency(app: App):
    """测试并发"""
    from nonebot_plugin_user import get_user, get_user_by_id

    users: list[tuple[str, str]] = [
        ("qq", "1"),
        ("qq", "2"),
        ("qq", "3"),
    ]

    async def do_check():
        platform, platform_id = random.choice(users)

        user = await get_user(platform, platform_id)
        assert user.name == f"{platform}-{platform_id}"

        user_loaded = await get_user_by_id(user.id)
        assert user_loaded.id == user.id

    tasks = []
    for _ in range(0, 100):
        tasks.append(asyncio.create_task(do_check()))
    await asyncio.gather(*tasks)


async def test_permission_concurrency(app: App):
    """测试权限和其他响应器同时访问数据库"""
    from nonebot_plugin_orm import get_session

    from tests.plugins.orm import orm_cmd

    async with get_session() as session:
        from tests.plugins.orm import Test

        test = await session.scalars(select(Test))

        assert len(test.all()) == 0

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_group_message_event_v11(message=Message("/orm"))
        ctx.receive_event(bot, event)
        ctx.should_call_api("get_group_info", {"group_id": 10000}, {})
        ctx.should_call_api("get_group_member_info", {"group_id": 10000, "user_id": 10, "no_cache": True}, {})
        ctx.should_call_send(event, "已提交！", None)
        ctx.should_finished(orm_cmd)

    async with get_session() as session:
        from tests.plugins.orm import Test

        test = await session.scalars(select(Test))

        assert len(test.all()) == 1

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)

        event = fake_group_message_event_v11(message=Message("/orm"))
        ctx.receive_event(bot, event)
        ctx.should_call_send(event, "已提交！", None)
        ctx.should_finished(orm_cmd)

    async with get_session() as session:
        from tests.plugins.orm import Test

        test = await session.scalars(select(Test))

        assert len(test.all()) == 2
