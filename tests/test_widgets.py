import pytest

from totp_auth.auth_widgets import PasswordWidget, TOTPWidget
from totp_auth.errors import (
    InvalidCredentials,
    InvalidFields,
    FieldError,
    FieldErrorList,
)


def test_password_widget():
    widget = PasswordWidget()
    with pytest.raises(InvalidCredentials):
        widget.check_data({"login": "325346", "password": "admin"})

    with pytest.raises(InvalidFields):
        widget.check_data({"admin": "admin"})

    with pytest.raises(
        FieldError,
        match=f"(<FieldErrorList.INCORRECT_LENGTH: 'INCORRECT_LENGTH'>, 'login')",
    ):
        widget.check_data({"login": "admin" * 100, "password": "admin"})

    widget.check_data({"login": "admin", "password": "admin"})


def test_totp_widget():
    widget = TOTPWidget()
    with pytest.raises(InvalidFields):
        widget.check_data({"login": "admin"})

    with pytest.raises(
        FieldError,
        match=f"(<FieldErrorList.INCORRECT_LENGTH: 'INCORRECT_LENGTH'>, 'login')",
    ):
        widget.check_data({"login": "admin" * 100, "code": "admin"})

    with pytest.raises(InvalidFields):
        widget.check_data({"login": "admin", "password": "admin"})

    widget.check_data({"login": "admin", "code": "123456"})
