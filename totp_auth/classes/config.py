from configparser import ConfigParser, DuplicateSectionError
from contextlib import suppress
from dataclasses import dataclass
import secrets

from pyotp import TOTP


@dataclass
class ServerConfig:
    name: str
    listen: str
    redirect: str
    headers_rewrite: dict[str, str]
    users: dict[str, TOTP]

    @property
    def listen_data(self) -> tuple[str, int]:
        if ":" in self.listen:
            raw = self.listen.split(":")
            return raw[0], int(raw[1])
        else:
            return self.listen, 80

    @property
    def redirect_data(self) -> tuple[str, int]:
        if ":" in self.redirect:
            raw = self.redirect.split(":")
            return raw[0], int(raw[1])
        else:
            return self.redirect, 80


class Config:
    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.config = ConfigParser()
        self.config.read(filename)

    def save(self) -> None:
        with open(self.filename, "w") as f:
            self.config.write(f)

    def reset_secret_token(self) -> None:
        self.config.set("DEFAULT", "secret_token", secrets.token_hex(16))

    def secret_token(self) -> str:
        return self.config.get("DEFAULT", "secret_token")

    def add_server(self, server: ServerConfig) -> None:
        with suppress(DuplicateSectionError):
            self.config.add_section(server.name)

        self.config.set(server.name, "listen", server.listen)
        self.config.set(server.name, "redirect", server.redirect)

        for h, v in server.headers_rewrite.items():
            self.config.set(server.name, f"header_{h.lower()}", v)

        for u, v in server.users.items():
            self.config.set(server.name, f"user_{u.lower()}", v.secret)

    def delete_server(self, name: str) -> None:
        self.config.remove_section(name)

    def get_server(self, name: str) -> ServerConfig:
        headers_rewrite = {}
        users = {}
        for j in self.config[name]:
            if j.startswith("header_"):
                headers_rewrite[j[7:].capitalize()] = self.config.get(name, j)
            elif j.startswith("user_"):
                users[j[5:]] = TOTP(self.config.get(name, j))

        return ServerConfig(
            name=name,
            listen=self.config.get(name, "listen"),
            redirect=self.config.get(name, "redirect"),
            headers_rewrite=headers_rewrite,
            users=users,
        )

    def list_servers(self) -> list[ServerConfig]:
        servers = []
        for i in self.config:
            if i == "DEFAULT":
                continue
            servers.append(self.get_server(i))

        return servers
