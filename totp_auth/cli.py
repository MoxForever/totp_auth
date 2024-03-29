import argparse
import asyncio
from contextlib import suppress
from pathlib import Path
import os
import secrets

import pyotp

from totp_auth.classes.db_config import AppConfig, Server, Database
from totp_auth.server import start_server_async
from totp_auth.utils import parse_host_port


async def user_cli(args: argparse.Namespace, config: AppConfig):
    raise NotImplemented("Not ready yet")


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


async def reset_token(config: AppConfig):
    config.secret_token = secrets.token_hex(16)
    await config.save()
    print("Secret token has been reset")
    return True


async def cli():
    cfg_path = Path.home() / ".config" / "totp-auth"
    os.makedirs(cfg_path, exist_ok=True)
    db = Database(cfg_path / "config.sqlite")
    await db.connect()
    await db.migrate()

    config = await db.get_config()

    # Root
    parser = argparse.ArgumentParser(description="Reverse proxy with TOTP auth")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    subparsers.add_parser("run", help="Start the server")
    subparsers.add_parser("reset_token", help="Reset secret token")
    parser_server = subparsers.add_parser("server", help="Servers settings")
    parser_user = subparsers.add_parser("user", help="Users settings")

    # Server
    server_subparsers = parser_server.add_subparsers(
        dest="server", help="Servers config"
    )
    server_subparsers.add_parser("ls", help="List all servers")
    server_create = server_subparsers.add_parser("create", help="New server")
    server_update = server_subparsers.add_parser("update", help="Update server")
    server_delete = server_subparsers.add_parser("delete", help="Delete server")

    server_create.add_argument("listen", help="host[:port] format")
    server_create.add_argument("rewrite", help="host[:port] format")

    server_update.add_argument("id", help="Server id")
    server_update.add_argument(
        "-l", "--listen", default=None, help="host[:port] format"
    )
    server_update.add_argument(
        "-r", "--rewrite", default=None, help="host[:port] format"
    )

    server_delete.add_argument("id", help="Server id")

    # User
    users_subparsers = parser_user.add_subparsers(dest="user", help="Servers config")
    users_subparsers.add_parser("create", help="New server")
    users_subparsers.add_parser("delete", help="Delete user")

    args = parser.parse_args()
    with suppress(KeyboardInterrupt):
        executed = False
        if args.command == "run":
            executed = await start_server_async(config)
        elif args.command == "reset_token":
            executed = await reset_token(config)
        elif args.command == "server":
            executed = await server_cli(args, config)
        elif args.command == "user":
            executed = await user_cli(args, config)

        if not executed:
            return print("Unknown command, use -h for help")


def main():
    asyncio.run(cli())


if __name__ == "__main__":
    main()
