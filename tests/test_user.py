# ruff: noqa: E501
import pytest
from nonebot import get_adapter
from nonebot.adapters.onebot.v11 import Adapter, Bot, Message
from nonebug import App

from tests.fake import fake_group_message_event_v11, fake_private_message_event_v11


async def test_user(app: App, patch_current_time):
    """获取用户信息"""
    from nonebot_plugin_user.matchers import get_user_by_id, user_cmd

    with patch_current_time("2023-09-14 10:46:10", tick=False):
        async with app.test_matcher(user_cmd) as ctx:
            adapter = get_adapter(Adapter)
            bot = ctx.create_bot(base=Bot, adapter=adapter)
            event = fake_group_message_event_v11(message=Message("/user"))

            ctx.receive_event(bot, event)
            ctx.should_call_send(
                event,
                "平台名：qq\n平台 ID：10\n用户名：qq-10\n创建日期：2023-09-14 18:46:10+08:00",
                True,
            )
            ctx.should_finished(user_cmd)

        async with app.test_matcher(user_cmd) as ctx:
            adapter = get_adapter(Adapter)
            bot = ctx.create_bot(base=Bot, adapter=adapter)
            event = fake_private_message_event_v11(message=Message("/user"))

            ctx.receive_event(bot, event)
            ctx.should_call_send(
                event,
                "平台名：qq\n平台 ID：10\n用户名：qq-10\n创建日期：2023-09-14 18:46:10+08:00",
                True,
            )
            ctx.should_finished(user_cmd)

    user = await get_user_by_id(1)
    assert user.id == 1

    with pytest.raises(ValueError, match="找不到用户信息"):
        await get_user_by_id(2)


async def test_user_set_name(app: App, patch_current_time):
    """设置用户名"""
    from nonebot_plugin_user.matchers import set_user_name, user_cmd

    with patch_current_time("2023-09-14 10:46:10", tick=False):
        async with app.test_matcher(user_cmd) as ctx:
            adapter = get_adapter(Adapter)
            bot = ctx.create_bot(base=Bot, adapter=adapter)
            event = fake_group_message_event_v11(message=Message("/user"))

            ctx.receive_event(bot, event)
            ctx.should_call_send(
                event,
                "平台名：qq\n平台 ID：10\n用户名：qq-10\n创建日期：2023-09-14 18:46:10+08:00",
                True,
            )
            ctx.should_finished(user_cmd)

        async with app.test_matcher(user_cmd) as ctx:
            adapter = get_adapter(Adapter)
            bot = ctx.create_bot(base=Bot, adapter=adapter)
            event = fake_group_message_event_v11(message=Message("/user"), user_id=1)

            ctx.receive_event(bot, event)
            ctx.should_call_send(
                event,
                "平台名：qq\n平台 ID：1\n用户名：qq-1\n创建日期：2023-09-14 18:46:10+08:00",
                True,
            )
            ctx.should_finished(user_cmd)

        async with app.test_matcher(user_cmd) as ctx:
            adapter = get_adapter(Adapter)
            bot = ctx.create_bot(base=Bot, adapter=adapter)
            event = fake_private_message_event_v11(message=Message("/user -l qq-1"))

            ctx.receive_event(bot, event)
            ctx.should_call_send(
                event,
                "用户名修改失败，用户名已存在",
                True,
            )
            ctx.should_finished(user_cmd)

        async with app.test_matcher(user_cmd) as ctx:
            adapter = get_adapter(Adapter)
            bot = ctx.create_bot(base=Bot, adapter=adapter)
            event = fake_private_message_event_v11(message=Message("/user -l name"))

            ctx.receive_event(bot, event)
            ctx.should_call_send(
                event,
                "用户名修改成功",
                True,
            )
            ctx.should_finished(user_cmd)

        async with app.test_matcher(user_cmd) as ctx:
            adapter = get_adapter(Adapter)
            bot = ctx.create_bot(base=Bot, adapter=adapter)
            event = fake_group_message_event_v11(message=Message("/user"))

            ctx.receive_event(bot, event)
            ctx.should_call_send(
                event,
                "平台名：qq\n平台 ID：10\n用户名：name\n创建日期：2023-09-14 18:46:10+08:00",
                True,
            )
            ctx.should_finished(user_cmd)

    with pytest.raises(ValueError, match="找不到用户信息"):
        await set_user_name("123", "qq", "not exist")


async def test_user_session(app: App, patch_current_time):
    """用户会话相关的测试"""
    from nonebot import on_command

    from nonebot_plugin_user import UserSession

    test_matcher = on_command("test")

    @test_matcher.handle()
    async def _(session: UserSession):
        await test_matcher.finish(session.group_session_id)

    with patch_current_time("2023-09-14 10:46:10", tick=False):
        async with app.test_matcher(test_matcher) as ctx:
            adapter = get_adapter(Adapter)
            bot = ctx.create_bot(base=Bot, adapter=adapter)
            event = fake_group_message_event_v11(message=Message("/test"))

            ctx.receive_event(bot, event)
            ctx.should_call_send(event, "qq_10000", True)
            ctx.should_finished(test_matcher)
