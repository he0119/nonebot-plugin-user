from nonebot import require
from sqlalchemy import String, select

require("nonebot_plugin_alconna")
require("nonebot_plugin_orm")
from nonebot.params import Depends
from nonebot_plugin_alconna import Alconna, on_alconna
from nonebot_plugin_orm import Model, get_scoped_session
from sqlalchemy.ext.asyncio import async_scoped_session
from sqlalchemy.orm import Mapped, mapped_column


class Test(Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    bot_id: Mapped[str] = mapped_column(String(64))


orm_cmd = on_alconna(
    Alconna("orm"),
    use_cmd_start=True,
)


@orm_cmd.handle()
async def handle_orm(
    session: async_scoped_session = Depends(get_scoped_session),
):
    await session.scalars(select(Test))

    session.add(Test(bot_id="test"))
    await session.commit()
    await orm_cmd.finish("已提交！")
