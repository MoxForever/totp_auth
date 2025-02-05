from abc import ABC, abstractmethod
from types import SimpleNamespace
from typing import Generic, TypeVar

from totp_auth.utils import get_secret_key
from totp_auth.core.loaders.translations import WidgetLanguage
from totp_auth.core.errors import InvalidFields
from totp_auth.core.utils import generate_csrf_token, check_csrf_token

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
        body = "".join(field.render(lang) for field in self.fields)
        csrf_token = generate_csrf_token(get_secret_key())
        return f"""<input type="hidden" name="csrf" value="{csrf_token}">{body}"""

    def check_data(self, data: dict[str, str]):
        csrf_token = data.pop("csrf", None)
        if not csrf_token or not check_csrf_token(csrf_token, get_secret_key()):
            raise InvalidFields("CSRF token is invalid")

        checked_data = {}
        for field in self.fields:
            if field.name not in data:
                raise InvalidFields(f"Field {field.name} is missing")
            checked_data[field.name] = field.check_field(data[field.name])

        self._check_data(
            SimpleNamespace(**checked_data)  # pyright: ignore[reportArgumentType]
        )
