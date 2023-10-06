import datetime
from contextlib import contextmanager

import nonebot
import pytest
from freezegun import freeze_time
from nonebot.adapters.onebot.v11 import Adapter as OnebotV11Adapter
from nonebug import NONEBOT_INIT_KWARGS, App
from sqlalchemy import delete, event


def pytest_configure(config: pytest.Config) -> None:
    config.stash[NONEBOT_INIT_KWARGS] = {
        "sqlalchemy_database_url": "sqlite+aiosqlite:///:memory:",
        "alembic_startup_check": False,
    }


@pytest.fixture(scope="session", autouse=True)
def load_adapters(nonebug_init: None):
    driver = nonebot.get_driver()
    driver.register_adapter(OnebotV11Adapter)


@pytest.fixture
async def app(app: App):
    # 加载插件
    nonebot.require("nonebot_plugin_user")
    from nonebot_plugin_orm import get_session, init_orm

    await init_orm()

    yield app

    # 清理数据库

    from nonebot_plugin_user.models import Bind, User

    async with get_session() as session, session.begin():
        await session.execute(delete(Bind))
        await session.execute(delete(User))

    # UserInfo 有自己的缓存，所以要清理
    from nonebot_plugin_userinfo.getter import _user_info_cache

    _user_info_cache.clear()


@pytest.fixture
async def session(app: App):
    from nonebot_plugin_orm import get_scoped_session

    Session = get_scoped_session()

    async with Session() as session:
        yield session


# https://stackoverflow.com/questions/29116718/how-to-mocking-created-time-in-sqlalchemy
@contextmanager
def patch_time(time_to_freeze, tick=True):
    from nonebot_plugin_user.models import User

    with freeze_time(time_to_freeze, tick=tick) as frozen_time:

        def set_timestamp(mapper, connection, target):
            now = datetime.datetime.utcnow()
            if hasattr(target, "created_at"):
                target.created_at = now

        event.listen(User, "before_insert", set_timestamp, propagate=True)
        yield frozen_time
        event.remove(User, "before_insert", set_timestamp)


@pytest.fixture(scope="function")
def patch_current_time():
    return patch_time
