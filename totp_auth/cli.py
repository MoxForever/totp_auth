import argparse
from contextlib import suppress

import pyotp

from .classes.config import Config, ServerConfig
from .server import start_server


def choose_server_cli(config: Config):
    servers = config.list_servers()
    for i, s in enumerate(servers):
        print(f"{i+1}. {s.name}")

    while True:
        s_id = input("Choose server id - ")
        if s_id.isnumeric():
            s_id = int(s_id)
            if s_id <= len(servers):
                break
    return servers[s_id - 1]


def user_cli(args: argparse.Namespace, config: Config):
    if args.user == "create":
        server = choose_server_cli(config)
        username = input("Choose username - ")
        code = pyotp.TOTP(pyotp.random_base32())
        print(f"Add code to your 2fa app - {code.secret}, 6 digit, SHA1")
        while True:
            test = input("Verify code from application - ")
            if code.verify(test):
                break
        server.users[username] = code
        config.add_server(server)
        print("Ready!")
    elif args.user == "delete":
        server = choose_server_cli(config)
        username = input("Choose username - ")
        if username not in server.users:
            print("User does not exists")
            return
        del server.users[username]
        config.add_server(server)
    else:
        print("Unknown command, use -h for help")
        return


def server_cli(args: argparse.Namespace, config: Config):
    if args.server == "ls":
        servers = config.list_servers()
        if len(servers) > 0:
            for i in servers:
                print(f"{i.name}: {i.listen} -> {i.redirect}")
        else:
            print(f"No servers configured")
    elif args.server == "create":
        name = input("Server name - ")
        listen = input("Listen address host:[port] - ")
        redirect = input("Redirect address host:[port] - ")
        config.add_server(ServerConfig(name, listen, redirect, {}, {}))
    elif args.server == "update":
        try:
            server = config.get_server(args.name)
        except KeyError:
            print(f"Server {args.name} does not exists")
            return

        try:
            k, v = args.data.split("=", 1)
        except ValueError:
            print("Expected key=value format")
            return

        config.delete_server(server.name)
        setattr(server, k, v)
        print("Updated!")
        config.add_server(server)
    else:
        print("Unknown command, use -h for help")
        return


def main():
    config = Config("config.ini")

    parser = argparse.ArgumentParser(description="Reverse proxy with TOTP auth")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    subparsers.add_parser("run", help="Start the server")

    subparsers.add_parser("reset_token", help="Reset secret token")

    parser_server = subparsers.add_parser("server", help="Set server address")
    server_subparsers = parser_server.add_subparsers(
        dest="server", help="Servers config"
    )

    server_subparsers.add_parser("ls", help="List all servers")
    server_subparsers.add_parser("create", help="New server")
    update_server = server_subparsers.add_parser("update", help="Update server")
    update_server.add_argument("name", type=str, help="Server name")
    update_server.add_argument("data", type=str, help="Key for change, key=value")

    parser_users = subparsers.add_parser("user", help="User login settings")
    users_subparsers = parser_users.add_subparsers(dest="user", help="Servers config")
    users_subparsers.add_parser("create", help="New server")
    users_subparsers.add_parser("delete", help="Delete user")

    args = parser.parse_args()

    with suppress(KeyboardInterrupt):
        if args.command == "run":
            start_server(config)
        elif args.command == "reset_token":
            config.reset_secret_token()
            print("Secret token has been reset")
        elif args.command == "server":
            server_cli(args, config)
        elif args.command == "user":
            user_cli(args, config)
        else:
            print("Unknown command, use -h for help")
            return

        config.save()


if __name__ == "__main__":
    main()
