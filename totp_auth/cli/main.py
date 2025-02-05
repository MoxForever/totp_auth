from argparse import ArgumentParser

from .api import TotpHttpApi
from .subparsers import servers


def main():
    api = TotpHttpApi(port=8000)

    parser = ArgumentParser(description="TOTP Auth CLI for configure server")
    parser.set_defaults(func=lambda args: parser.print_help())

    subparsers = parser.add_subparsers()
    server_parser = subparsers.add_parser("servers", help="Server configuration")
    servers(server_parser, api)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
