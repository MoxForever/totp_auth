from dataclasses import dataclass


@dataclass
class Server:
    id: int
    name: str
    theme_name: str
    language: str
    widgets: list[str]
