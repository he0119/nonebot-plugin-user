"""init db

修订 ID: ac57f7074e58
父修订:
创建时间: 2023-10-07 18:17:40.861103

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "ac57f7074e58"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = ("nonebot_plugin_user",)
depends_on: str | Sequence[str] | None = None


def upgrade(name: str = "") -> None:
    if name:
        return
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "nonebot_plugin_user_user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_nonebot_plugin_user_user")),
        sa.UniqueConstraint("name", name=op.f("uq_nonebot_plugin_user_user_name")),
    )
    op.create_table(
        "nonebot_plugin_user_bind",
        sa.Column("platform", sa.String(length=32), nullable=False),
        sa.Column("platform_id", sa.String(length=64), nullable=False),
        sa.Column("bind_id", sa.Integer(), nullable=False),
        sa.Column("original_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["bind_id"],
            ["nonebot_plugin_user_user.id"],
            name=op.f("fk_nonebot_plugin_user_bind_bind_id_nonebot_plugin_user_user"),
        ),
        sa.ForeignKeyConstraint(
            ["original_id"],
            ["nonebot_plugin_user_user.id"],
            name=op.f(
                "fk_nonebot_plugin_user_bind_original_id_nonebot_plugin_user_user"
            ),
        ),
        sa.PrimaryKeyConstraint(
            "platform", "platform_id", name=op.f("pk_nonebot_plugin_user_bind")
        ),
    )
    # ### end Alembic commands ###


def downgrade(name: str = "") -> None:
    if name:
        return
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("nonebot_plugin_user_bind")
    op.drop_table("nonebot_plugin_user_user")
    # ### end Alembic commands ###
