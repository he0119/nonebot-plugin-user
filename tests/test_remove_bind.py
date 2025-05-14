import pytest
from nonebot import get_adapter
from nonebot.adapters.onebot.v11 import Adapter, Bot, Message
from nonebug import App
from pytest_mock import MockerFixture
from sqlalchemy import select

from tests.fake import fake_private_message_event_v11


async def test_remove_bind(app: App, patch_current_time, mocker: MockerFixture):
    """解除绑定"""
    from nonebot_plugin_orm import get_session

    from nonebot_plugin_user.matchers import bind_cmd
    from nonebot_plugin_user.models import Bind, User

    with patch_current_time("2023-09-14 10:46:10", tick=False):
        async with get_session(expire_on_commit=False) as session:
            user = User(id=1, name="nickname")
            user2 = User(id=2, name="nickname2")
            session.add(user)
            session.add(user2)
            await session.commit()
            bind = Bind(platform_id="1", platform="QQClient", bind_id=user.id, original_id=user.id)
            bind2 = Bind(platform_id="10", platform="QQClient", bind_id=user.id, original_id=user2.id)
            session.add(bind)
            session.add(bind2)
            await session.commit()

        async with app.test_matcher(bind_cmd) as ctx:
            adapter = get_adapter(Adapter)
            bot = ctx.create_bot(base=Bot, adapter=adapter)
            event = fake_private_message_event_v11(message=Message("/bind -r"))

            ctx.receive_event(bot, event)
            ctx.should_call_send(
                event,
                "解绑成功",
                True,
            )
            ctx.should_finished(bind_cmd)

        async with get_session() as session:
            bind = (await session.scalars(select(Bind).where(Bind.platform_id == 10))).one()
            assert bind.bind_id == 2


async def test_remove_bind_self(app: App, patch_current_time, mocker: MockerFixture):
    """解除最初的绑定"""
    from nonebot_plugin_user.matchers import bind_cmd

    with patch_current_time("2023-09-14 10:46:10", tick=False):
        async with app.test_matcher(bind_cmd) as ctx:
            adapter = get_adapter(Adapter)
            bot = ctx.create_bot(base=Bot, adapter=adapter)
            event = fake_private_message_event_v11(message=Message("/bind -r"))

            ctx.receive_event(bot, event)
            ctx.should_call_send(
                event,
                "不能解绑最初绑定的账号",
                True,
            )
            ctx.should_finished(bind_cmd)


async def test_bind_not_exist(app: App):
    """不存在的账户"""
    from nonebot_plugin_user.utils import remove_bind, set_bind

    with pytest.raises(ValueError, match="找不到用户信息"):
        await remove_bind("QQClient", "1")

    with pytest.raises(ValueError, match="找不到用户信息"):
        await set_bind("QQClient", "1", 2)
