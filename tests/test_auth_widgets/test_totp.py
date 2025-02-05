import pytest
from totp_auth.auth_widgets.totp import TOTPWidget, TOTPWidgetData
from totp_auth.core.errors import InvalidCredentials


def test_check_data_valid():
    widget = TOTPWidget()
    data = TOTPWidgetData(login="admin", code=123456)
    assert widget._check_data(data) == True


def test_check_data_invalid():
    widget = TOTPWidget()
    data = TOTPWidgetData(login="user", code=654321)
    with pytest.raises(InvalidCredentials):
        widget._check_data(data)


def test_check_data_invalid_field_data():
    widget = TOTPWidget()
    data = TOTPWidgetData(login="admin", code=654321)
    with pytest.raises(InvalidCredentials):
        widget._check_data(data)


def test_check_data_missing_login():
    widget = TOTPWidget()
    data = TOTPWidgetData(login="", code=123456)
    with pytest.raises(InvalidCredentials):
        widget._check_data(data)


def test_check_data_missing_code():
    widget = TOTPWidget()
    data = TOTPWidgetData(login="admin", code=0)
    with pytest.raises(InvalidCredentials):
        widget._check_data(data)
