import asyncio
import datetime
from contextlib import contextmanager
from pathlib import Path

import nonebot
import pytest
from freezegun import freeze_time
from nonebot.adapters.onebot.v11 import Adapter as OnebotV11Adapter
from nonebot.adapters.onebot.v12 import Adapter as OnebotV12Adapter
from nonebug import NONEBOT_INIT_KWARGS, App
from pytest_mock import MockerFixture
from sqlalchemy import delete, event


def pytest_configure(config: pytest.Config) -> None:
    config.stash[NONEBOT_INIT_KWARGS] = {
        "sqlalchemy_database_url": "sqlite+aiosqlite:///:memory:",
        "alembic_startup_check": False,
    }


@pytest.fixture(scope="session", autouse=True)
def _load_adapters(nonebug_init: None):
    driver = nonebot.get_driver()
    driver.register_adapter(OnebotV11Adapter)
    driver.register_adapter(OnebotV12Adapter)


@pytest.fixture
async def app(app: App, mocker: MockerFixture, tmp_path: Path):
    # 加载插件
    nonebot.require("nonebot_plugin_user")
    nonebot.require("tests.plugins.admin")
    nonebot.require("tests.plugins.orm")
    from nonebot_plugin_orm import get_session, init_orm

    mocker.patch("nonebot_plugin_orm._data_dir", tmp_path / "orm")
    # 确保 _insert_mutex 是在当前事件循环中创建的
    mocker.patch("nonebot_plugin_user.utils._insert_mutex", asyncio.Lock())

    await init_orm()

    yield app

    # 清理数据库

    from nonebot_plugin_user.models import Bind, User

    async with get_session() as session, session.begin():
        await session.execute(delete(Bind))
        await session.execute(delete(User))


@pytest.fixture
async def session(app: App):
    from nonebot_plugin_orm import get_session

    async with get_session() as session:
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


@pytest.fixture
def patch_current_time():
    return patch_time
