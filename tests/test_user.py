import pytest
from nonebot import get_adapter
from nonebot.adapters.onebot.v11 import Adapter, Bot, Message
from nonebug import App

from tests.fake import fake_group_message_event_v11, fake_private_message_event_v11


async def test_user(app: App, patch_current_time):
    """获取用户信息"""
    from nonebot_plugin_user import get_user_by_id, user_cmd

    with patch_current_time("2023-09-14 10:46:10", tick=False):
        async with app.test_matcher(user_cmd) as ctx:
            adapter = get_adapter(Adapter)
            bot = ctx.create_bot(base=Bot, adapter=adapter)
            event = fake_group_message_event_v11(message=Message("/user"))

            ctx.receive_event(bot, event)
            ctx.should_call_send(
                event,
                Message("平台：qq\n平台 ID：10\n用户名：qq-10\n创建日期：2023-09-14 10:46:10"),
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
                Message("平台：qq\n平台 ID：10\n用户名：qq-10\n创建日期：2023-09-14 10:46:10"),
                True,
            )
            ctx.should_finished(user_cmd)

    user = await get_user_by_id(1)
    assert user.id == 1

    with pytest.raises(ValueError):
        await get_user_by_id(2)
