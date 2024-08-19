from nonebot import get_driver, require
from nonebot.adapters import Bot
from nonebot.permission import Permission

require("nonebot_plugin_user")
require("nonebot_plugin_alconna")
from nonebot_plugin_alconna import Alconna, on_alconna

from nonebot_plugin_user import User

config = get_driver().config


def is_superuser(user: User) -> bool:
    """检查当前用户是否属于超级管理员"""
    return user.name in config.superusers


class SuperUser:
    """检查当前事件是否属于超级管理员"""

    __slots__ = ()

    def __repr__(self) -> str:
        return "Superuser()"

    async def __call__(self, bot: Bot, user: User) -> bool:
        return user.name in bot.config.superusers


SUPERUSER: Permission = Permission(SuperUser())
"""匹配任意超级用户事件"""

superuser_cmd = on_alconna(
    Alconna("superuser"),
    permission=SUPERUSER,
    use_cmd_start=True,
)


@superuser_cmd.handle()
async def handle_superuser():
    await superuser_cmd.finish("你是超级用户！")
