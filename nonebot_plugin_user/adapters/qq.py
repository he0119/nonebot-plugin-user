from typing import TYPE_CHECKING, List

from ..consts import SessionLevel
from ..extractor import Extractor
from ..models import Session, Subject

if TYPE_CHECKING:
    from nonebot.adapters.qq import Bot, Event

OFFER_BY = "nonebot_plugin_user"

PRESET_ROLES = {2: "guild_admin", 4: "guild_owner", 5: "channel_admin"}

PRESET_ROLE_PRIORITY = (4, 2, 5)


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

    def get_subjects(self, bot: "Bot", event: "Event") -> List[Subject]:
        from nonebot.adapters.qq import AtMessageCreateEvent, MessageCreateEvent

        if not isinstance(event, (AtMessageCreateEvent, MessageCreateEvent)):
            return []

        guild_id = event.guild_id
        channel_id = event.channel_id
        member = event.member

        if member is None or member.roles is None:
            return []

        subjects = []
        for actual_role in sorted(member.roles):
            if actual_role in PRESET_ROLES:
                # 我们默认优先级高的预置角色（例如服务器主）
                # 继承优先级低的（例如频道管理员）
                priority = PRESET_ROLE_PRIORITY.index(actual_role)
                for i in range(priority, len(PRESET_ROLE_PRIORITY)):
                    role = PRESET_ROLE_PRIORITY[i]

                    if role == 5:  # 频道管理员
                        subjects.append(
                            Subject(
                                content=f"qqguild:g{guild_id}:c{channel_id}.{PRESET_ROLES[role]}",
                                offer_by=OFFER_BY,
                                tag=f"qqguild:guild:channel.{PRESET_ROLES[role]}",
                            )
                        )
                        subjects.append(
                            Subject(
                                content=f"qqguild:c{channel_id}.{PRESET_ROLES[role]}",
                                offer_by=OFFER_BY,
                                tag=f"qqguild:channel:{PRESET_ROLES[role]}",
                            )
                        )
                    else:
                        subjects.append(
                            Subject(
                                content=f"qqguild:g{guild_id}.{PRESET_ROLES[role]}",
                                offer_by=OFFER_BY,
                                tag=f"qqguild:guild.{PRESET_ROLES[role]}",
                            )
                        )
                    subjects.append(
                        Subject(
                            content=f"qqguild:{PRESET_ROLES[role]}",
                            offer_by=OFFER_BY,
                            tag=f"qqguild:{PRESET_ROLES[role]}",
                        )
                    )
            else:
                subjects.append(
                    Subject(
                        content=f"qqguild:g{guild_id}.role_{actual_role}",
                        offer_by=OFFER_BY,
                        tag="qqguild:guild.role",
                    )
                )

        return subjects
