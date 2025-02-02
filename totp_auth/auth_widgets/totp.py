from typing import Literal

from totp_auth.models import AuthWidget
from totp_auth.models.fields import InputTextField, InputNumericField
from totp_auth.utils.errors import InvalidCredentials
from totp_auth.utils.translator import Language


class TOTPWidgetData:
    login: str
    code: str


class TOTPWidget(AuthWidget[TOTPWidgetData]):
    name = "totp"
    fields = [
        InputTextField("login", "login", 64),
        InputNumericField("code", "code", 6),
    ]

    def _check_data(self, data: TOTPWidgetData) -> Literal[True]:
        if data.login == "admin" and data.code == "admin":
            return True
        raise InvalidCredentials("Invalid credentials")
