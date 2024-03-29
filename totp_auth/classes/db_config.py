import asyncio
from dataclasses import dataclass
import os
from pathlib import Path
import secrets

import aiosqlite


@dataclass
class User:
    id: int
    username: str
    totp_secret: str
    app_config: "AppConfig"
    access_to_servers: dict[int, "Server"]


@dataclass
class HeaderRewrite:
    id: int
    value: str
    header: str
    server: "Server"
    app_config: "AppConfig"


@dataclass
class Server:
    id: int
    listen_host: str
    listen_port: int
    rewrite_host: str
    rewrite_port: int
    app_config: "AppConfig"
    users_with_access: dict[int, User]
    headers_rewrite: dict[int, HeaderRewrite]


@dataclass
class AppConfig:
    secret_token: str
    servers: dict[int, Server]
    users: dict[int, User]
    database: "Database"


class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None

    async def connect(self):
        self.connection = await aiosqlite.connect(self.db_path)

    async def migrate(self):
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
                if (await cursor.fetchone())[0] == 0:
                    print(f"Migration {i} applied")
                    with open(migrations_dir / i, "r") as f:
                        await cursor.executescript(f.read())
                        await cursor.execute("INSERT INTO migrations VALUES (?)", (i,))
            await self.connection.commit()

    async def close(self):
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

            # Servers fetch
            servers = {}
            await cursor.execute("SELECT * FROM server")
            for i in await cursor.fetchall():
                server = Server(*i, {}, {})
                servers[server.id] = server

            # Users fetch
            users = {}
            await cursor.execute("SELECT * FROM user")
            for i in await cursor.fetchall():
                user = User(*i, app_config, {})
                users[user.id] = user

            app_config = AppConfig(
                secret_token=secret_token, servers=servers, users=users, database=self
            )

            # Fetch servers-users relation
            users_to_server: dict[int, list[int]] = {}
            await cursor.execute("SELECT * FROM users_access")
            for i in await cursor.fetchall():
                if i[1] in users_to_server:
                    users_to_server[i[1]].append(i[0])
                else:
                    users_to_server[i[1]] = [i[0]]

            servers_to_user: dict[int, list[int]] = {}
            for u_id, s_id in users_to_server.items():
                if s_id in servers_to_user:
                    servers_to_user[s_id].append(u_id)
                else:
                    servers_to_user[s_id] = [u_id]

            # Filling empty fields
            for user in app_config.users.values():
                user.access_to_servers = [servers[i] for i in servers_to_user[user.id]]

            for server in app_config.servers.values():
                server.users_with_access = [
                    users[i] for i in users_to_server[server.id]
                ]

            # Headers rewrite fill
            await cursor.execute("SELECT * FROM header_rewrite")
            for rewrite_rule in await cursor.fetchall():
                rule = HeaderRewrite(
                    *rewrite_rule[:-1], servers[rewrite_rule[-1]], app_config
                )
                servers[rule.server.id][rule.id] = rule

        return app_config


async def main():
    db = Database("data.db")
    await db.connect()
    await db.migrate()
    print(await db.get_config())


asyncio.run(main())
