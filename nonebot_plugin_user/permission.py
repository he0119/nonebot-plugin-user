from typing import List

from nonebot.adapters import Bot
from nonebot.params import Depends
from nonebot.permission import Permission

from nonebot_plugin_user.models import Subject

from .params import extract_subjects


class SuperUser:
    """检查当前事件是否是消息事件且属于超级管理员"""

    __slots__ = ()

    def __repr__(self) -> str:
        return "Superuser()"

    async def __call__(
        self,
        bot: Bot,
        subjects: List[Subject] = Depends(extract_subjects),
    ) -> bool:
        return any(subject.content in bot.config.superusers for subject in subjects)


SUPERUSER: Permission = Permission(SuperUser())
"""匹配任意超级用户事件"""
