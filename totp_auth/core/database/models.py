from typing import Any
from pydantic import BaseModel


class ProxyData(BaseModel):
    host: str
    port: int


class Server(BaseModel):
    id: int
    name: str
    theme_name: str
    language: str
    widgets: list[str]

    proxy_from: ProxyData
    proxy_to: ProxyData


class User(BaseModel):
    id: int
    login: str
    is_superadmin: bool = False


class WidgetUserSettings(BaseModel):
    id: int
    user_id: int
    widget_name: str
    data: dict[str, Any]
