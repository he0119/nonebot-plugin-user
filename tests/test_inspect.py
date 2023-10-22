from nonebot import get_adapter
from nonebot.adapters.onebot.v11 import Adapter, Bot, Message
from nonebot.adapters.onebot.v12 import Adapter as AdapterV12
from nonebot.adapters.onebot.v12 import Bot as BotV12
from nonebot.adapters.onebot.v12 import Message as MessageV12
from nonebug import App

from tests.fake import fake_channel_message_event_v12, fake_group_message_event_v11


async def test_inspect(app: App):
    """获取会话信息"""
    from nonebot_plugin_user.matchers import inspect_cmd

    async with app.test_matcher() as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)
        event = fake_group_message_event_v11(message=Message("/inspect"))

        ctx.receive_event(bot, event)
        ctx.should_call_send(
            event,
            "平台名：qq\n平台 ID：10\n自身 ID：test\n群组 ID：10000",
            True,
        )
        ctx.should_finished(inspect_cmd)

    async with app.test_matcher() as ctx:
        adapter = get_adapter(AdapterV12)
        bot = ctx.create_bot(base=BotV12, adapter=adapter, impl="test", platform="test")
        event = fake_channel_message_event_v12(message=MessageV12("/inspect"))

        ctx.receive_event(bot, event)
        ctx.should_call_send(
            event,
            "平台名：test\n平台 ID：10\n自身 ID：test\n频道 ID：10000\n群组 ID：100000",
            True,
        )
        ctx.should_finished(inspect_cmd)
