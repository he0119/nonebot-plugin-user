import random
from typing import Dict, Optional, Tuple, cast

from expiringdict import ExpiringDict
from nonebot.adapters import Bot
from nonebot_plugin_alconna import (
    Alconna,
    AlconnaQuery,
    Args,
    Match,
    Option,
    Query,
    on_alconna,
)
from nonebot_plugin_session import SessionLevel
from sqlalchemy.exc import IntegrityError

from .annotated import UserSession as UserSession
from .config import plugin_config
from .utils import get_user as get_user
from .utils import get_user_by_id as get_user_by_id
from .utils import remove_bind, set_bind, set_user_name

user_cmd = on_alconna(
    Alconna(
        "user",
        Option("-l", Args["name", str]),
    ),
    use_cmd_start=True,
)


@user_cmd.handle()
async def _(session: UserSession, name: Match[str]):
    if name.available:
        try:
            await set_user_name(session.platform, session.platform_id, name.result)
        except IntegrityError:
            await user_cmd.finish("用户名修改失败，用户名已存在")
        else:
            await user_cmd.finish("用户名修改成功")

    await user_cmd.finish(
        "\n".join(
            [
                f"平台名：{session.platform}",
                f"平台 ID：{session.platform_id}",
                f"用户名：{session.user_name}",
                f"创建日期：{session.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
            ]
        )
    )


inspect_cmd = on_alconna(Alconna("inspect"), use_cmd_start=True)


@inspect_cmd.handle()
async def _(bot: Bot, session: UserSession):
    msgs = [
        f"平台名：{session.platform}",
        f"平台 ID：{session.platform_id}",
        f"自身 ID：{bot.self_id}",
    ]

    if session.level == SessionLevel.LEVEL3:
        msgs.append(f"频道 ID：{session.session.id3}")
    if session.level != SessionLevel.LEVEL1:
        msgs.append(f"群组 ID：{session.session.id2}")

    await inspect_cmd.finish("\n".join(msgs))


tokens = cast(
    Dict[str, Tuple[str, str, int, Optional[SessionLevel]]],
    ExpiringDict(max_len=100, max_age_seconds=300),
)


def generate_token() -> str:
    return f"{plugin_config.user_token_prefix}{random.randint(100000, 999999)}"


bind_cmd = on_alconna(
    Alconna("bind", Option("-r"), Args["token?", str]), use_cmd_start=True
)


@bind_cmd.handle()
async def _(
    session: UserSession,
    token: Optional[str] = None,
    remove: Query[bool] = AlconnaQuery("r.value", default=False),
):
    if remove.result:
        result = await remove_bind(session.platform, session.platform_id)
        if result:
            await bind_cmd.finish("解绑成功")
        else:
            await bind_cmd.finish("不能解绑最初绑定的账号")

    # 生成令牌
    if not token:
        token = generate_token()
        tokens[token] = (
            session.platform,
            session.platform_id,
            session.user_id,
            session.level,
        )
        await bind_cmd.finish(
            f"命令 bind 可用于在多个平台间绑定用户数据。绑定过程中，原始平台的用户数据将完全保留，而目标平台的用户数据将被原始平台的数据所覆盖。\n请确认当前平台是你的目标平台，并在 5 分钟内使用你的账号在原始平台内向机器人发送以下文本：\n/bind {token}\n绑定完成后，你可以随时使用「bind -r」来解除绑定状态。"  # noqa: E501
        )

    # 绑定流程
    if token in tokens:
        # 平台的相关信息
        platform, platform_id, user_id, level = tokens.pop(token)
        # 群内绑定的第一步，会在原始平台发送令牌
        # 此时 platform_id 和 platform 为目标平台的信息
        if level == SessionLevel.LEVEL2 or level == SessionLevel.LEVEL3:
            token = generate_token()
            tokens[token] = (session.platform, session.platform_id, user_id, None)
            await bind_cmd.finish(
                f"令牌核验成功！下面将进行第二步操作。\n请在 5 分钟内使用你的账号在目标平台内向机器人发送以下文本：\n/bind {token}\n注意：当前平台是你的原始平台，这里的用户数据将覆盖目标平台的数据。"  # noqa: E501
            )
        # 群内绑定的第二步，会在目标平台发送令牌
        # 此时 platform_id 和 platform 为原始平台的信息
        # 需要重新获取其用户信息，然后将目标平台绑定至原始平台
        elif level is None:
            if session.user_id != user_id:
                await bind_cmd.finish("请使用最开始要绑定账号进行操作")

            user = await get_user(platform, platform_id)
            await set_bind(session.platform, session.platform_id, user.id)
            await bind_cmd.finish("绑定成功")
        # 私聊绑定时，会在原始平台发送令牌
        # 此时 platform_id 和 platform 为目标平台的信息
        # 直接将目标平台绑定至原始平台
        elif level == SessionLevel.LEVEL1:
            await set_bind(platform, platform_id, session.user_id)
            await bind_cmd.finish("绑定成功")
    else:
        await bind_cmd.finish("令牌不存在或已过期")
