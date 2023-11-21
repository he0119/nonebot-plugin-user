import asyncio
import random
from typing import List, Tuple

from nonebug import App


async def test_concurrency(app: App):
    from nonebot_plugin_user import get_user, get_user_by_id

    users: List[Tuple[str, str]] = [
        ("qq", "1"),
        ("qq", "2"),
        ("qq", "3"),
    ]

    async def do_check():
        platform, platform_id = random.choice(users)

        user = await get_user(platform, platform_id)
        assert user.name == f"{platform}-{platform_id}"

        user_loaded = await get_user_by_id(user.id)
        assert user_loaded.id == user.id

    tasks = []
    for _ in range(0, 100):
        tasks.append(asyncio.create_task(do_check()))
    await asyncio.gather(*tasks)
