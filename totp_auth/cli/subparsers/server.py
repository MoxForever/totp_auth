from argparse import ArgumentParser

from totp_auth.cli.api.base import TotpHttpApi


def servers_list(list_parser: ArgumentParser, api: TotpHttpApi):
    def execute():
        for server in api.server_list():
            print(f"{server.id}: {server.name}")

    list_parser.set_defaults(func=lambda args: execute())


def servers(server_parser: ArgumentParser, api: TotpHttpApi):
    server_parser.set_defaults(func=lambda args: server_parser.print_help())

    subparsers = server_parser.add_subparsers()
    server_parser = subparsers.add_parser("list", help="List servers")
    servers_list(server_parser, api)
