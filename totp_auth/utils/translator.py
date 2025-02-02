import json
from pathlib import Path
from collections import defaultdict


class Language:
    def __init__(self, name: str, data: dict, prekey: str = ""):
        self.name = name
        self.data = data
        self.prekey = prekey

    def __call__(self, *key: str) -> str:
        key_parts = ".".join(key).split(".")
        if self.prekey:
            key_parts = self.prekey.split(".") + key_parts

        result: dict | str = self.data
        for part in key_parts:
            if isinstance(result, str):
                raise ValueError("Translate path is invalid")
            try:
                result = result[part]
            except KeyError:
                full_key = ".".join(key)
                raise ValueError(f"Translate path is invalid: {full_key}")

        if isinstance(result, dict):
            raise ValueError("Translate path is invalid")

        return result

    def sublang(self, *keys: str) -> "Language":
        return Language(self.name, self.data, ".".join(keys))

    def get_lang_for_widget(self, widget_name: str) -> "WidgetLanguage":
        return WidgetLanguage(self.sublang("auth_widgets", widget_name), widget_name)


class WidgetLanguage(Language):
    def __init__(self, lang: Language, widget_name: str):
        super().__init__(lang.name, lang.data, lang.prekey)
        self.widget_name = widget_name


class Translator:
    def __init__(self, *languages_dirs: str):
        self._langs: dict[str, dict] = defaultdict(dict)
        for languages_dir in languages_dirs:
            for lang_file in Path(languages_dir).glob("*.json"):
                lang_data = self._load_language(lang_file)
                self._langs[lang_file.stem].update(lang_data)

    def _load_language(self, path: Path) -> dict:
        with open(path, "r") as f:
            return json.load(f)

    def get_language(self, name: str) -> Language:
        return Language(name, self._langs[name])

    def list_languages(self) -> list[str]:
        return list(self._langs.keys())
