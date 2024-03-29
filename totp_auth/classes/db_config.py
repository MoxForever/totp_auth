from dataclasses import dataclass
import os
from pathlib import Path
import secrets

import aiosqlite
from pyotp import TOTP


@dataclass
class User:
    id: int | None
    username: str
    _totp_secret: str
    app_config: "AppConfig"
    access_to_servers: dict[int, "Server"]

    @property
    def totp(self) -> TOTP:
        return TOTP(self._totp_secret)


@dataclass
class HeaderRewrite:
    id: int | None
    value: str
    header: str
    server: "Server"
    app_config: "AppConfig"


@dataclass
class Server:
    id: int | None
    listen_host: str
    listen_port: int
    rewrite_host: str
    rewrite_port: int
    app_config: "AppConfig"
    users_with_access: dict[int, User]
    headers_rewrite: dict[int, HeaderRewrite]

    @property
    def listen(self):
        return f"{self.listen_host}:{self.listen_port}"

    @property
    def rewrite(self):
        return f"{self.rewrite_host}:{self.rewrite_port}"


@dataclass
class AppConfig:
    secret_token: str
    servers: dict[int, Server]
    users: dict[int, User]
    database: "Database"

    async def save(self):
        await self.database.save_app_config(self)


class Database:
    def __init__(self, db_path: str | Path):
        self.db_path = db_path
        self.connection = None

    async def connect(self) -> None:
        self.connection = await aiosqlite.connect(self.db_path)

    async def migrate(self) -> None:
        async with self.connection.cursor() as cursor:
            migrations_dir = Path(__file__).parent.parent / "migrations"
            with open(migrations_dir / "_default.sql", "r") as f:
                await cursor.executescript(f.read())

            for i in os.listdir(migrations_dir):
                if i.startswith("_"):
                    continue

                await cursor.execute(
                    "SELECT count(1) FROM migrations WHERE name = ?", (i,)
                )
                data = await cursor.fetchone()
                if not (data and data[0] > 0):
                    with open(migrations_dir / i, "r") as f:
                        await cursor.executescript(f.read())
                        await cursor.execute("INSERT INTO migrations VALUES (?)", (i,))
            await self.connection.commit()

    async def close(self) -> None:
        if self.connection:
            await self.connection.close()

    async def get_config(self) -> AppConfig:
        async with self.connection.cursor() as cursor:
            # AppConfig fetch
            await cursor.execute("SELECT * FROM app_config")

            row = await cursor.fetchone()
            if row is None:
                secret_token = secrets.token_hex(16)
                await cursor.execute(
                    "INSERT INTO app_config VALUES (?)", (secret_token,)
                )
                await self.connection.commit()
            else:
                secret_token = row[0]

            app_config = AppConfig(
                secret_token=secret_token, servers={}, users={}, database=self
            )

            # Servers fetch
            servers = {}
            await cursor.execute("SELECT * FROM servers")
            for i in await cursor.fetchall():
                server = Server(
                    *i,
                    app_config=app_config,
                    users_with_access={},
                    headers_rewrite={},
                )
                servers[server.id] = server

            # Users fetch
            users = {}
            await cursor.execute("SELECT * FROM users")
            for i in await cursor.fetchall():
                user = User(*i, app_config=app_config, access_to_servers={})
                users[user.id] = user

            app_config.users = users
            app_config.servers = servers

            # Fetch servers-users relation
            users_to_server: dict[int, list[int]] = {}
            await cursor.execute("SELECT * FROM users_access")
            for i in await cursor.fetchall():
                if i[1] in users_to_server:
                    users_to_server[i[1]].append(i[0])
                else:
                    users_to_server[i[1]] = [i[0]]

            servers_to_user: dict[int, list[int]] = {}
            for s_id, u_id in users_to_server.items():
                for user in u_id:
                    if user in servers_to_user:
                        servers_to_user[user].append(s_id)
                    else:
                        servers_to_user[user] = [s_id]

            # Filling empty fields
            for user in app_config.users.values():
                user.access_to_servers = [servers[i] for i in servers_to_user[user.id]]

            for server in app_config.servers.values():
                server.users_with_access = [
                    users[i] for i in users_to_server[server.id]
                ]

            # Headers rewrite fill
            await cursor.execute("SELECT * FROM headers_rewrite")
            for rewrite_rule in await cursor.fetchall():
                rule = HeaderRewrite(
                    *rewrite_rule[:-1],
                    server=servers[rewrite_rule[-1]],
                    app_config=app_config,
                )
                servers[rule.server.id][rule.id] = rule

        return app_config

    async def save_app_config(self, config: AppConfig) -> None:
        async with self.connection.cursor() as cursor:
            # appconfig save
            await cursor.execute(
                "UPDATE app_config SET secret_token = ?", (config.secret_token,)
            )

            # users save
            await cursor.execute("SELECT id FROM users")
            db_users_ids: set[int] = {i[0] for i in await cursor.fetchall()}
            for key, user in config.users.items():
                if user.id is None:
                    await cursor.execute(
                        "INSERT INTO users (username, totp_secret) VALUES "
                        "(?, ?) RETURNING id",
                        (user.username, user._totp_secret),
                    )
                    row = await cursor.fetchone()
                    if row:
                        user_id = row[0]
                        del config.users[key]
                        user.id = user_id
                        config.users[user_id] = user

                else:
                    db_users_ids.remove(user.id)
                    await cursor.execute(
                        "UPDATE users SET username = ?, totp_secret = ? WHERE id = ?",
                        (user.username, user._totp_secret, user.id),
                    )

            for user_id in db_users_ids:
                await cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))

            # servers save
            await cursor.execute("SELECT id FROM servers")
            db_servers_ids: set[int] = {i[0] for i in await cursor.fetchall()}
            for key, server in config.servers.items():
                if server.id is None:
                    await cursor.execute(
                        "INSERT INTO servers (listen_host, listen_port, "
                        "rewrite_host, rewrite_port) VALUES (?, ?) RETURNING id",
                        (
                            server.listen_host,
                            server.listen_port,
                            server.rewrite_host,
                            server.rewrite_port,
                        ),
                    )
                    row = await cursor.fetchone()
                    if row:
                        server_id = row[0]
                        del config.servers[key]
                        server.id = server_id
                        config.servers[server_id] = server

                else:
                    db_servers_ids.remove(server.id)
                    await cursor.execute(
                        "UPDATE servers SET listen_host = ?, listen_port = ?, "
                        "rewrite_host = ?, rewrite_port = ? WHERE id = ?",
                        (
                            server.listen_host,
                            server.listen_port,
                            server.rewrite_host,
                            server.rewrite_port,
                            server.id,
                        ),
                    )

            for server_id in db_servers_ids:
                await cursor.execute("DELETE FROM servers WHERE id = ?", (server_id,))

            # headers rewrite

            await cursor.execute("SELECT id FROM headers_rewrite")
            db_headers_ids: set[int] = {i[0] for i in await cursor.fetchall()}
            for server in config.servers.values():
                for key, header in server.headers_rewrite.items():
                    if header.id is None:
                        await cursor.execute(
                            "INSERT INTO headers_rewrite (value, header, "
                            "server_id) VALUES (?, ?, ?) RETURNING id",
                            (header.value, header.header, server.id),
                        )
                        row = await cursor.fetchone()
                        if row:
                            header_id = row[0]
                            del server.headers_rewrite[key]
                            header.id = header_id
                            server.headers_rewrite[header_id] = header

                    else:
                        db_headers_ids.remove(header.id)
                        await cursor.execute(
                            "UPDATE headers_rewrite SET value = ?, header = ?, "
                            "server_id = ? WHERE id = ?",
                            (header.value, header.header, server.id, header.id),
                        )

            for header_id in db_headers_ids:
                await cursor.execute("DELETE FROM servers WHERE id = ?", (server_id,))