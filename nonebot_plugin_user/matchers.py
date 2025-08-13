import random
import re
from typing import Optional

from expiringdictx import ExpiringDict
from nonebot_plugin_alconna import (
    Alconna,
    AlconnaQuery,
    Args,
    CommandMeta,
    Match,
    Option,
    Query,
    on_alconna,
)
from nonebot_plugin_uninfo import SceneType
from sqlalchemy.exc import IntegrityError

from .annotated import UserSession as UserSession
from .config import plugin_config
from .utils import get_user as get_user
from .utils import get_user_by_id as get_user_by_id
from .utils import remove_bind, set_bind, set_user_email, set_user_name


def is_valid_email(email: str) -> bool:
    """简单的邮箱格式验证"""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


user_cmd = on_alconna(
    Alconna(
        "user",
        Option("-l|--name", Args["name", str], help_text="修改用户名"),
        Option("-e|--email", Args["email", str], help_text="修改邮箱"),
        meta=CommandMeta(
            description="查看或修改用户信息",
            example=("查看用户信息\n/user\n修改用户名\n/user -l [用户名]\n修改邮箱\n/user -e [邮箱]"),
        ),
    ),
    use_cmd_start=True,
    block=True,
)


@user_cmd.handle()
async def _(session: UserSession, name: Match[str], email: Match[str]):
    if name.available:
        try:
            await set_user_name(session.platform, session.platform_user.id, name.result)
        except IntegrityError:
            await user_cmd.finish("用户名修改失败，该用户名已被使用")
        else:
            await user_cmd.finish("用户名修改成功")

    if email.available:
        if not is_valid_email(email.result):
            await user_cmd.finish("邮箱格式不正确，请输入有效的邮箱地址")

        await set_user_email(session.platform, session.platform_user.id, email.result)
        await user_cmd.finish("邮箱修改成功")

    # 显示用户信息时包含邮箱
    user_info = [
        f"平台名：{session.platform}",
        f"平台 ID：{session.platform_user.id}",
        f"用户名：{session.user_name}",
        f"邮箱：{session.user_email or '未设置'}",
        f"创建日期：{session.created_at.astimezone()}",
    ]

    await user_cmd.finish("\n".join(user_info))


tokens = ExpiringDict[str, tuple[str, str, int, Optional[SceneType]]](capacity=100, default_age=300)


def generate_token() -> str:
    return f"{plugin_config.user_token_prefix}{random.randint(100000, 999999)}"


bind_cmd = on_alconna(
    Alconna(
        "bind",
        Option("-r", help_text="解除绑定"),
        Args["token?", str],
        meta=CommandMeta(description="绑定用户", example="绑定用户\n/bind\n解除绑定\n/bind -r"),
    ),
    use_cmd_start=True,
    block=True,
)


@bind_cmd.handle()
async def _(
    session: UserSession,
    token: Optional[str] = None,
    remove: Query[bool] = AlconnaQuery("r.value", default=False),
):
    if remove.result:
        result = await remove_bind(session.platform, session.platform_user.id)
        if result:
            await bind_cmd.finish("解绑成功")
        else:
            await bind_cmd.finish("不能解绑最初绑定的账号")

    # 生成令牌
    if not token:
        token = generate_token()
        tokens[token] = (
            session.platform,
            session.platform_user.id,
            session.user_id,
            session.type,
        )
        await bind_cmd.finish(
            f"命令 bind 可用于在多个平台间绑定用户数据。绑定过程中，原始平台的用户数据将完全保留，而目标平台的用户数据将被原始平台的数据所覆盖。\n请确认当前平台是你的目标平台，并在 5 分钟内使用你的账号在原始平台内向机器人发送以下文本：\n/bind {token}\n绑定完成后，你可以随时使用「bind -r」来解除绑定状态。"  # noqa: E501
        )

    # 绑定流程
    bind_info = tokens.pop(token)
    if bind_info is None:
        await bind_cmd.finish("令牌不存在或已过期")

    # 平台的相关信息
    platform, user_id, uid, scene_type = bind_info
    # 群内绑定的第一步，会在原始平台发送令牌
    # 此时 user_id 和 platform 为目标平台的信息
    if scene_type is not None and scene_type.value:
        token = generate_token()
        tokens[token] = (session.platform, session.platform_user.id, uid, None)
        await bind_cmd.finish(
            f"令牌核验成功！下面将进行第二步操作。\n请在 5 分钟内使用你的账号在目标平台内向机器人发送以下文本：\n/bind {token}\n注意：当前平台是你的原始平台，这里的用户数据将覆盖目标平台的数据。"  # noqa: E501
        )
    # 群内绑定的第二步，会在目标平台发送令牌
    # 此时 user_id 和 platform 为原始平台的信息
    # 需要重新获取其用户信息，然后将目标平台绑定至原始平台
    elif scene_type is None:
        if session.user_id != uid:
            await bind_cmd.finish("请使用最开始要绑定账号进行操作")

        user = await get_user(platform, user_id)
        await set_bind(session.platform, session.platform_user.id, user.id)
        await bind_cmd.finish("绑定成功")
    # 私聊绑定时，会在原始平台发送令牌
    # 此时 platform_id 和 platform 为目标平台的信息
    # 直接将目标平台绑定至原始平台
    else:
        await set_bind(platform, user_id, session.user_id)
        await bind_cmd.finish("绑定成功")
