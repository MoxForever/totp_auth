import base64
import hashlib
from typing import Optional

from .classes.config import Config


def _create_cookie_token(data: str, config: Config) -> str:
    return hashlib.sha256(f"{data}.{config.secret_token()}".encode("utf-8")).hexdigest()


def create_cookie(data: str, config: Config) -> str:
    token = _create_cookie_token(data, config)
    return base64.b64encode(data.encode("utf-8")).decode("utf-8") + "." + token


def get_cookie_data(cookie: str, config: Config) -> Optional[str]:
    raw = cookie.split(".", 1)
    if len(raw) != 2:
        return None
    raw_data, token = raw
    data = base64.b64decode(raw_data).decode("utf-8")
    if token != _create_cookie_token(data, config):
        return None
    else:
        return data
