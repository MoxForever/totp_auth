from dataclasses import dataclass

from totp_auth.models import AuthWidget


@dataclass
class Server:
    name: str
    theme_name: str
    language: str
    widgets: list[AuthWidget]
