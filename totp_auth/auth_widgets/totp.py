from dataclasses import dataclass
from typing import Literal

from totp_auth.core.models import AuthWidget, InputTextField, InputNumericField
from totp_auth.core.errors import InvalidCredentials


@dataclass
class TOTPWidgetData:
    login: str
    code: int


class TOTPWidget(AuthWidget[TOTPWidgetData]):
    name = "totp"
    fields = [
        InputTextField("login", "login", 64),
        InputNumericField("code", "code", 6),
    ]

    def _check_data(self, data: TOTPWidgetData) -> Literal[True]:
        if data.login == "admin" and data.code == 123456:
            return True
        raise InvalidCredentials("Invalid credentials")


__all__ = ["TOTPWidget"]
