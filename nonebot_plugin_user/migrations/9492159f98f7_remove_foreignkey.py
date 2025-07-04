"""remove foreignkey

迁移 ID: 9492159f98f7
父迁移: ac57f7074e58
创建时间: 2023-11-18 11:57:00.764269

"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op
from nonebot import logger

revision: str = "9492159f98f7"
down_revision: str | Sequence[str] | None = "ac57f7074e58"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade(name: str = "") -> None:
    if name:
        return
    # ### commands auto generated by Alembic - please adjust! ###

    # 尝试删除外键约束
    # 老的数据库中还有约束，但是新的没有，所以这里可能会报错
    try:
        with op.get_context().autocommit_block():
            # 删除操作放在独立事务中，因为可能会报错
            # 不独立事务会导致 Alembic 在执行时出错
            with op.batch_alter_table("nonebot_plugin_user_bind", schema=None) as batch_op:
                batch_op.drop_constraint(
                    "fk_nonebot_plugin_user_bind_original_id_nonebot_plugin_user_user",
                    type_="foreignkey",
                )
                batch_op.drop_constraint(
                    "fk_nonebot_plugin_user_bind_bind_id_nonebot_plugin_user_user",
                    type_="foreignkey",
                )
            logger.info("[user] 已成功删除外键约束")
    except Exception:
        logger.debug("[user] 未找到外键约束，跳过删除")
    # ### end Alembic commands ###


def downgrade(name: str = "") -> None:
    if name:
        return
    # ### commands auto generated by Alembic - please adjust! ###

    # ### end Alembic commands ###
