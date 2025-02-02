import re
from types import NoneType
from typing import Generic, Protocol, TypeVar

from totp_auth.utils.errors import FieldError, FieldErrorList
from totp_auth.utils.translator import WidgetLanguage


ReturnType = TypeVar("ReturnType")


class Field(Protocol, Generic[ReturnType]):
    name: str
    return_type: type[ReturnType]

    def render(self, lang: WidgetLanguage) -> str: ...

    def check_field(self, data: str) -> ReturnType: ...


class InputTextField(Field[str]):
    return_type = str

    def __init__(
        self,
        name: str,
        label_translate_path: str,
        max_length: int = 64,
        auto_lower: bool = True,
    ):
        self.name = name
        self.label_translate_path = label_translate_path
        self.max_length = max_length
        self.auto_lower = auto_lower

    def render(self, lang: WidgetLanguage) -> str:
        label = lang(self.label_translate_path)
        return f"""<div class="input-field input-field-text">
                        <label for="{self.name}">{label}</label>
                        <input 
                            type="text"
                            name="{self.name}"
                            maxlength="{self.max_length}"
                            required>
                    </div>"""

    def check_field(self, data: str) -> str:
        if len(data) > self.max_length:
            raise FieldError(FieldErrorList.INCORRECT_LENGTH)
        return data if self.auto_lower else data.lower()


class InputPasswordField(Field[str]):
    return_type = str

    def __init__(self, name: str, label_translate_path: str, max_length: int = 64):
        self.name = name
        self.label_translate_path = label_translate_path
        self.max_length = max_length

    def render(self, lang: WidgetLanguage) -> str:
        label = lang(self.label_translate_path)
        return f"""<div class="input-field input-field-password">
                        <label for="{self.name}">{label}</label>
                        <input 
                            type="password"
                            name="{self.name}"
                            maxlength="{self.max_length}"
                            required/>
                    </div>"""

    def check_field(self, data: str) -> str:
        if len(data) > self.max_length:
            raise FieldError(FieldErrorList.INCORRECT_LENGTH)
        return data


class InputNumericField(Field[int]):
    return_type = int

    def __init__(self, name: str, label_translate_path: str, digits_count: int):
        self.name = name
        self.label_translate_path = label_translate_path
        self.digits_count = digits_count

    def _render_digit(self, index: int) -> str:
        return f"""<input 
                    type="number"
                    data-custom-type="numeric-digit"
                    name="{self.name}-{index}"
                    id="{self.name}-{index}"
                    min="0" max="9" required/>"""

    def render(self, lang: WidgetLanguage) -> str:
        label = lang(self.label_translate_path)
        digits_html = "".join(self._render_digit(i) for i in range(self.digits_count))
        return f"""<div class="input-field input-field-numeric">
                        <label for="{self.name}">{label}</label>
                        <input
                            type="hidden"
                            name="{self.name}"
                            data-custom-type="numeric"/>
                            <div class="input-field-numeric-digits">{digits_html}</div>
                    </div>"""

    def check_field(self, data: str) -> int:
        if not data.isdigit():
            raise FieldError(FieldErrorList.NOT_DIGIT)
        if len(data) != self.digits_count:
            raise FieldError(FieldErrorList.INCORRECT_LENGTH)
        return int(data)


class InputEmailField(Field[str]):
    return_type = str

    def __init__(self, name: str, label_translate_path: str):
        self.name = name
        self.label_translate_path = label_translate_path

    def render(self, lang: WidgetLanguage) -> str:
        label = lang(self.label_translate_path)
        return f"""<div class="input-field input-field-email">
                        <label for="{self.name}">{label}</label>
                        <input 
                            type="email"
                            name="{self.name}"
                            required/>
                    </div>"""

    def check_field(self, data: str) -> str:
        if len(data) > 320:
            raise FieldError(FieldErrorList.INCORRECT_LENGTH)
        if re.fullmatch(r"[a-z0-9]{1,}@[a-z0-9]{1,}\.[a-z]{1,}", data) is None:
            raise FieldError(FieldErrorList.EMAIL_NOT_VALID)
        return data


class LabelOnlyField(Field[None]):
    return_type = NoneType

    def __init__(self, label: str):
        self.label = label

    def render(self) -> str:
        return f"""<div class="input-field input-field-label-only">
                        <label>{self.label}</label>
                    </div>"""

    def check_field(self, _: None) -> None:
        return None
