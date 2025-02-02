from abc import ABC, abstractmethod
from types import SimpleNamespace
from typing import Generic, TypeVar

from totp_auth.loaders import WidgetLanguage
from totp_auth.errors import InvalidFields

from .fields import Field

ReturnType = TypeVar("ReturnType")


class AuthWidget(ABC, Generic[ReturnType]):
    name: str
    fields: list[Field]

    @abstractmethod
    def _check_data(self, data: ReturnType) -> None:
        raise NotImplementedError

    def get_method_text(self, lang: WidgetLanguage) -> str:
        return lang("method_button")

    def render(self, lang: WidgetLanguage) -> str:
        return "".join(field.render(lang) for field in self.fields)

    def check_data(self, data: dict[str, str]):
        checked_data = {}
        for field in self.fields:
            if field.name not in data:
                raise InvalidFields(f"Field {field.name} is missing")
            checked_data[field.name] = field.check_field(data[field.name])

        self._check_data(
            SimpleNamespace(**checked_data)  # pyright: ignore[reportArgumentType]
        )
