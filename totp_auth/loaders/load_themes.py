from dataclasses import dataclass
from pathlib import Path


@dataclass
class Theme:
    name: str
    css: str


class ThemesLoader:
    def __init__(self, *themes_dirs: Path):
        self._themes_dirs = themes_dirs
        self._themes: dict[str, Theme] = {}
        self.reload()

    def reload(self):
        self._themes.clear()
        for themes_dir in self._themes_dirs:
            for theme_src in themes_dir.glob("*.css"):
                theme = self._load_theme(theme_src)
                self._themes[theme.name] = theme

    @staticmethod
    def _load_theme(path: Path) -> Theme:
        with open(path, "r") as f:
            data = f.read().strip()
            if not data.startswith("/*") or "*/" not in data:
                raise ValueError(f"Invalid theme file: {path}")

            metadata_raw = data.split("*/")[0].strip("/*")
            metadata_lines = [
                i[2:].split(":") for i in metadata_raw.split("\n") if i.startswith("- ")
            ]
            metadata = {k.strip(): v.strip() for k, v in metadata_lines}

            return Theme(metadata["name"], data)

    def get_theme(self, name: str) -> Theme:
        return self._themes[name]

    def list_themes(self) -> list[str]:
        return list(self._themes.keys())
