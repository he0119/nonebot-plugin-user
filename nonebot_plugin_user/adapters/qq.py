from typing import TYPE_CHECKING, List

from ..consts import SessionLevel
from ..extractor import Extractor
from ..models import Session

if TYPE_CHECKING:
    from nonebot.adapters.qq import Bot, Event


class QQExtractor(Extractor["Bot", "Event"]):
    @classmethod
    def get_adapter(cls) -> str:
        return "QQ"

    def get_session(self, bot: "Bot", event: "Event") -> Session:
        from nonebot.adapters.qq import (
            AtMessageCreateEvent,
            C2CMessageCreateEvent,
            DirectMessageCreateEvent,
            GroupAtMessageCreateEvent,
            MessageCreateEvent,
        )

        platform = "unknown"
        level = SessionLevel.LEVEL0
        id1 = event.get_user_id()
        id2 = None
        id3 = None

        if isinstance(event, C2CMessageCreateEvent):
            platform = "qq"
            level = SessionLevel.LEVEL1
        elif isinstance(event, GroupAtMessageCreateEvent):
            platform = "qq"
            level = SessionLevel.LEVEL2
            id2 = event.group_id
        elif isinstance(event, (DirectMessageCreateEvent)):
            platform = "qqguild"
            level = SessionLevel.LEVEL1
        elif isinstance(event, (AtMessageCreateEvent, MessageCreateEvent)):
            platform = "qqguild"
            level = SessionLevel.LEVEL3
            id2 = event.channel_id
            id3 = event.guild_id

        return Session(
            bot_id=bot.self_id,
            bot_type=bot.type,
            platform=platform,
            level=level,
            id1=id1,
            id2=id2,
            id3=id3,
        )

    def get_subjects(self, bot: "Bot", event: "Event") -> List[str]:
        return super().get_subjects(bot, event)
