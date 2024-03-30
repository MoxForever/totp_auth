import argparse
import asyncio
from contextlib import suppress
from pathlib import Path
import os
import secrets
from typing import Optional

import pyotp

from totp_auth.classes.db_config import AppConfig, Server, User, HeaderRewrite, Database
from totp_auth.server import start_server_async
from totp_auth.utils import parse_host_port


def user_picker(data: str, config: AppConfig) -> Optional[User]:
    if data.isnumeric():
        return config.users.get(int(data))
    else:
        for i in config.users.values():
            if i.username == data:
                return i
        return None


async def user_cli(args: argparse.Namespace, config: AppConfig):
    if args.user == "ls":
        if len(config.users) > 0:
            for i in config.users.values():
                print(f"{i.id}: {i.username}")
        else:
            print("No users configured")

    elif args.user == "create":
        user = User(
            id=None,
            username=args.username,
            _totp_secret=pyotp.random_base32(),
            app_config=config,
            access_to_servers={},
        )

        print(f"Your TOTP secret: {user._totp_secret}")
        while True:
            code = input("Write code from your 2fa app for confirmation\n")
            if user.totp.verify(code):
                break

        config.users[-1] = user
        await config.save()

    elif args.user == "delete":
        user = user_picker(args.user_data, config)

        if user and user.id:
            del config.users[user.id]
            await config.save()
            print(f"User {user.id}:{user.username} deleted")
        else:
            print(f"User {args.user_data} not found")

    elif args.user == "access":
        user = user_picker(args.user_data, config)
        server = config.servers.get(args.server)
        access = args.state in ["true", "t"]

        if user is None or user.id is None:
            print("User incorrect")
        elif server is None or server.id is None:
            print("Server incorrect")
        else:
            if access:
                user.access_to_servers[server.id] = server
                server.users_with_access[user.id] = user
            else:
                del user.access_to_servers[server.id]
                del server.users_with_access[user.id]
            await config.save()
            if access:
                print("Access granted")
            else:
                print("Access rewoked")

    else:
        return False
    return True


async def server_cli(args: argparse.Namespace, config: AppConfig):
    if args.server == "ls":
        if len(config.servers) > 0:
            for server_id, server in config.servers.items():
                print(f"{server_id}: {server.listen} -> {server.rewrite}")
        else:
            print(f"No servers configured")

    elif args.server == "create":
        listen_host, listen_port = parse_host_port(args.listen)
        rewrite_host, rewrite_port = parse_host_port(args.rewrite)

        server = Server(
            id=None,
            listen_host=listen_host,
            listen_port=listen_port,
            rewrite_host=rewrite_host,
            rewrite_port=rewrite_port,
            app_config=config,
            users_with_access={},
            headers_rewrite={},
        )
        config.servers[-1] = server
        await config.save()
        print(f"Server {server.id} created")

    elif args.server == "update":
        server = config.servers[args.id]

        if args.listen:
            listen_host, listen_port = parse_host_port(args.listen)
            server.listen_host = listen_host
            server.listen_port = listen_port
        if args.rewrite:
            rewrite_host, rewrite_port = parse_host_port(args.rewrite)
            server.rewrite_host = rewrite_host
            server.rewrite_port = rewrite_port

        await config.save()
        print(f"Server {server.id} updated")

    elif args.server == "delete":
        del config.servers[args.id]
        await config.save()
        print(f"Server {args.id} deleted")

    else:
        return False

    return True


async def headers_cli(args: argparse.Namespace, config: AppConfig):
    if args.header == "ls":
        server = config.servers.get(args.server)
        if server is None or server.id is None:
            print("Invalid server")
        else:
            if len(server.headers_rewrite) > 0:
                for header in server.headers_rewrite.values():
                    print(f"{header.header} - {header.value}")
            else:
                print("No headers rewrite")

    elif args.header == "create":
        server = config.servers.get(args.server)
        if server is None or server.id is None:
            print("Invalid server")
        else:
            header = HeaderRewrite(
                id=None,
                value=args.value,
                header=args.header_data,
                server=server,
                app_config=config,
            )

            server.headers_rewrite[-1] = header
            await config.save()
            print(f"Rewrite {header.header}:{header.value} success")

    elif args.header == "delete":
        server = config.servers.get(args.server)
        if server is None or server.id is None:
            print("Invalid server")
        else:
            for key, header in server.headers_rewrite.items():
                if header.header == args.header_data:
                    del server.headers_rewrite[key]
                    await config.save()
                    break
            print(f"Rewrite {header.header}:{header.value} success")

    else:
        return False

    return True


async def reset_token(config: AppConfig):
    config.secret_token = secrets.token_hex(16)
    await config.save()
    print("Secret token has been reset")
    return True


def get_args() -> argparse.Namespace:
    # Root
    parser = argparse.ArgumentParser(description="Reverse proxy with TOTP auth")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    subparsers.add_parser("run", help="Start the server")
    subparsers.add_parser("reset_token", help="Reset secret token")
    parser_server = subparsers.add_parser("server", help="Servers settings")
    subparsers.add_parser("servers", help="Alias for 'server ls'").set_defaults(
        command="server", server="ls"
    )
    parser_user = subparsers.add_parser("user", help="Users settings")
    subparsers.add_parser("users", help="Alias for 'user ls'").set_defaults(
        command="user", user="ls"
    )
    parser_header = subparsers.add_parser("header", help="Users settings")

    # Server
    server_subparsers = parser_server.add_subparsers(
        dest="server", help="Servers config"
    )
    server_subparsers.add_parser("ls", help="List all servers")
    server_create = server_subparsers.add_parser("create", help="New server")
    server_update = server_subparsers.add_parser("update", help="Update server")
    server_delete = server_subparsers.add_parser("delete", help="Delete server")

    server_create.add_argument("listen", type=str, help="host[:port] format")
    server_create.add_argument("rewrite", type=str, help="host[:port] format")

    server_update.add_argument("id", type=int, help="Server id")
    server_update.add_argument(
        "-l", "--listen", type=str, default=None, help="host[:port] format"
    )
    server_update.add_argument(
        "-r", "--rewrite", type=str, default=None, help="host[:port] format"
    )

    server_delete.add_argument("id", type=int, help="Server id")

    # User
    users_subparsers = parser_user.add_subparsers(dest="user", help="Users config")
    users_subparsers.add_parser("ls", help="List all users")
    user_create = users_subparsers.add_parser("create", help="New user")
    user_delete = users_subparsers.add_parser("delete", help="Delete user")
    user_access = users_subparsers.add_parser("access", help="Give access to server")

    user_create.add_argument("username", type=str, help="User username")
    user_delete.add_argument("user_data", type=str, help="Id/username")

    user_access.add_argument("user_data", type=str, help="Id/username")
    user_access.add_argument("server", type=int, help="Server id")
    user_access.add_argument("state", type=str, help="true/false access to server")

    # Headers
    headers_subparser = parser_header.add_subparsers(
        dest="header", help="Headers config"
    )
    header_ls = headers_subparser.add_parser("ls", help="List all headers")
    header_create = headers_subparser.add_parser("create", help="Create new header")
    header_delete = headers_subparser.add_parser("delete", help="Delete header")

    header_ls.add_argument("server", type=int, help="Server id")

    header_create.add_argument("server", type=int, help="Server id")
    header_create.add_argument("header_data", type=str, help="Header name")
    header_create.add_argument("value", type=str, help="Header value")

    header_delete.add_argument("server", type=int, help="Server id")
    header_delete.add_argument("header_data", type=str, help="Header name")

    return parser.parse_args()


async def cli():
    with suppress(KeyboardInterrupt):
        cfg_path = Path.home() / ".config" / "totp-auth"
        os.makedirs(cfg_path, exist_ok=True)
        db = Database(cfg_path / "config.sqlite")
        await db.migrate()
        config = await db.get_config()

        args = get_args()
        executed = False
        if args.command == "run":
            executed = await start_server_async(config)
        elif args.command == "reset_token":
            executed = await reset_token(config)
        elif args.command == "server":
            executed = await server_cli(args, config)
        elif args.command == "user":
            executed = await user_cli(args, config)
        elif args.command == "header":
            executed = await headers_cli(args, config)

        if not executed:
            return print("Unknown command, use -h for help")


def main():
    asyncio.run(cli())


if __name__ == "__main__":
    main()
