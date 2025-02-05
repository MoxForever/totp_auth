from dataclasses import dataclass
from typing import Literal

from totp_auth.core.models import AuthWidget, InputTextField, InputPasswordField
from totp_auth.core.errors import InvalidCredentials


@dataclass
class PasswordWidgetData:
    login: str
    password: str


class PasswordWidget(AuthWidget[PasswordWidgetData]):
    name = "password"
    fields = [
        InputTextField("login", "login", 64),
        InputPasswordField("password", "password", 64),
    ]

    def _check_data(self, data: PasswordWidgetData) -> Literal[True]:
        if data.login == "admin" and data.password == "admin":
            return True
        raise InvalidCredentials("Invalid credentials")


__all__ = ["PasswordWidget"]
