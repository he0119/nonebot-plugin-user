"""migrate old plugin data

Revision ID: 0f0ca7421689
Revises: 8aa030575da8
Create Date: 2023-09-22 09:59:01.649159

"""
import sqlalchemy as sa
from alembic import op
from nonebot import logger
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

# revision identifiers, used by Alembic.
revision = "0f0ca7421689"
down_revision = "8aa030575da8"
branch_labels = None
depends_on = None


def _has_table(name: str) -> bool:
    from sqlalchemy import inspect

    insp = inspect(op.get_bind())
    return name in insp.get_table_names()


def upgrade() -> None:
    Base = automap_base()
    if _has_table("user_user") and _has_table("user_bind"):
        logger.info("发现旧版插件数据，开始迁移")
        Base.prepare(op.get_bind())
        OldUser = Base.classes.user_user
        OldBind = Base.classes.user_bind
        User = Base.classes.nonebot_plugin_user_user
        Bind = Base.classes.nonebot_plugin_user_bind
        with Session(op.get_bind()) as session:
            for old_user in session.query(OldUser):
                user = User(
                    id=old_user.id,
                    name=old_user.name,
                    created_at=old_user.created_at,
                )
                session.add(user)
            for old_bind in session.query(OldBind):
                bind = Bind(
                    pid=old_bind.pid,
                    platform=old_bind.platform,
                    aid=old_bind.aid,
                    bid=old_bind.bid,
                )
                session.add(bind)
            session.commit()


def downgrade() -> None:
    pass
