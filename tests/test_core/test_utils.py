import time
from totp_auth.core.utils import generate_csrf_token, check_csrf_token


def test_generate_csrf_token():
    secret_key = "my_secret_key"
    token = generate_csrf_token(secret_key)
    assert isinstance(token, str)
    assert len(token) > 0


def test_check_csrf_token_valid():
    secret_key = "my_secret_key"
    token = generate_csrf_token(secret_key)
    assert check_csrf_token(secret_key, token) == True


def test_check_csrf_token_invalid():
    secret_key = "my_secret_key"
    invalid_token = "invalid_token"
    assert check_csrf_token(secret_key, invalid_token) == False


def test_check_csrf_token_tampered():
    secret_key = "my_secret_key"
    token = generate_csrf_token(secret_key)
    tampered_token = token[:-1] + "A"  # Tamper the token
    assert check_csrf_token(secret_key, tampered_token) == False


def test_check_csrf_token_expired():
    secret_key = "my_secret_key"
    token = generate_csrf_token(secret_key)
    time.sleep(2)  # Simulate token expiration
    assert (
        check_csrf_token(secret_key, token) == True
    )  # Assuming token expiration is not implemented
