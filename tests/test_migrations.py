import sqlalchemy as sa


def test_refactor_uninfo_only_reflects_bind_table(monkeypatch):
    from nonebot_plugin_user.migrations import d6e05e49f79f_refactor_uninfo as migration

    engine = sa.create_engine("sqlite://")
    metadata = sa.MetaData()
    role_table = sa.Table(
        "nonebot_plugin_permission_rolemodel",
        metadata,
        sa.Column("id", sa.String(64), primary_key=True),
    )
    sa.Table(
        "nonebot_plugin_permission_roleinheritsmodel",
        metadata,
        sa.Column("role_id", sa.String(64), sa.ForeignKey(role_table.c.id), primary_key=True),
        sa.Column("parent_role_id", sa.String(64), sa.ForeignKey(role_table.c.id), primary_key=True),
    )
    bind_table = sa.Table(
        "nonebot_plugin_user_bind",
        metadata,
        sa.Column("platform", sa.String(32), primary_key=True),
        sa.Column("platform_id", sa.String(64), primary_key=True),
        sa.Column("bind_id", sa.Integer, nullable=False),
        sa.Column("original_id", sa.Integer, nullable=False),
    )
    metadata.create_all(engine)

    with engine.connect() as connection:
        connection.execute(
            sa.insert(bind_table),
            [
                {"platform": "qq", "platform_id": "123", "bind_id": 1, "original_id": 1},
                {"platform": "qq", "platform_id": "bot:123", "bind_id": 2, "original_id": 2},
                {"platform": "discord", "platform_id": "456", "bind_id": 3, "original_id": 3},
            ],
        )
        monkeypatch.setattr(migration.op, "get_bind", lambda: connection)

        migration.upgrade()

        platforms = set(connection.execute(sa.select(bind_table.c.platform)).scalars())
        assert platforms == {"QQClient", "QQAPI", "Discord"}

        migration.downgrade()

        platforms = set(connection.execute(sa.select(bind_table.c.platform)).scalars())
        assert platforms == {"qq", "qqguild", "discord"}
