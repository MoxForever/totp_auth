from dataclasses import dataclass
from pathlib import Path
from jinja2 import Template

from totp_auth.database import Server
from totp_auth.models import AuthWidget
from totp_auth.loaders import Translator, ThemesLoader, WidgetsLoader


def _load_file(file_path: Path) -> str:
    with file_path.open("r") as f:
        return f.read()


@dataclass
class AnotherWidget:
    name: str
    method_button: str


class PageRenderer:
    def __init__(
        self,
        themes_loader: ThemesLoader,
        translator: Translator,
        widgets_loader: WidgetsLoader,
    ):
        self.themes_loader = themes_loader
        self.translator = translator
        self.widgets_loader = widgets_loader

        dir_path = Path.cwd() / "totp_auth" / "static"
        self.template = Template(_load_file(dir_path / "index.html"))
        self.base_css = _load_file(dir_path / "style.css")
        self.base_js = _load_file(dir_path / "index.js")

    def _load_widgets(self, widgets_names: list[str]) -> dict[str, AuthWidget]:
        widgets = [
            self.widgets_loader.get_widget(widget_name) for widget_name in widgets_names
        ]
        return {widget.name: widget for widget in widgets}

    def render_for_server(
        self, server: Server, current_widget_name: str | None = None
    ) -> str:
        theme_css = self.themes_loader.get_theme(server.theme_name).css
        language = self.translator.get_language(server.language)

        widgets_dict = self._load_widgets(server.widgets)
        selected_widget = widgets_dict[current_widget_name or server.widgets[0]]
        selected_widget_html = selected_widget.render(
            language.get_lang_for_widget(selected_widget.name)
        )
        del widgets_dict[selected_widget.name]

        another_widgets = [
            AnotherWidget(
                widget.name,
                widget.get_method_text(language.get_lang_for_widget(widget.name)),
            )
            for widget in widgets_dict.values()
        ]

        return self.template.render(
            title=server.name,
            base_css=self.base_css,
            base_js=self.base_js,
            theme=theme_css,
            selected_widget_html=selected_widget_html,
            another_widgets=another_widgets,
            _=language.sublang("login_page"),
        )
