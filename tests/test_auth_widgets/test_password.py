import pytest
from totp_auth.auth_widgets.password import PasswordWidget, PasswordWidgetData
from totp_auth.core.errors import InvalidCredentials


def test_check_data_valid():
    widget = PasswordWidget()
    data = PasswordWidgetData(login="admin", password="admin")
    assert widget._check_data(data) == True


def test_check_data_invalid():
    widget = PasswordWidget()
    data = PasswordWidgetData(login="user", password="wrongpassword")
    with pytest.raises(InvalidCredentials):
        widget._check_data(data)


def test_check_data_invalid_field_data():
    widget = PasswordWidget()
    data = PasswordWidgetData(login="admin", password="wrongpassword")
    with pytest.raises(InvalidCredentials):
        widget._check_data(data)


def test_check_data_missing_login():
    widget = PasswordWidget()
    data = PasswordWidgetData(login="", password="admin")
    with pytest.raises(InvalidCredentials):
        widget._check_data(data)


def test_check_data_missing_password():
    widget = PasswordWidget()
    data = PasswordWidgetData(login="admin", password="")
    with pytest.raises(InvalidCredentials):
        widget._check_data(data)
