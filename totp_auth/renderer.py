from dataclasses import dataclass
from pathlib import Path
from jinja2 import Template

from totp_auth.database import Server
from totp_auth.models import AuthWidget
from totp_auth.utils.translator import Translator
from totp_auth.utils.load_themes import ThemesLoader


def _load_file(file_path: Path) -> str:
    with file_path.open("r") as f:
        return f.read()


@dataclass
class AnotherWidget:
    name: str
    method_button: str


class PageRenderer:
    def __init__(self, themes_loader: ThemesLoader, translator: Translator):
        self.themes_loader = themes_loader
        self.translator = translator

        dir_path = Path.cwd() / "totp_auth" / "static"
        self.template = Template(_load_file(dir_path / "index.html"))
        self.base_css = _load_file(dir_path / "style.css")
        self.base_js = _load_file(dir_path / "index.js")

    def render_for_server(
        self, server: Server, current_widget_name: str | None = None
    ) -> str:
        theme_css = self.themes_loader.get_theme(server.theme_name).css
        language = self.translator.get_language(server.language)

        selected_widget: AuthWidget | None = None
        if current_widget_name:
            for widget in server.widgets:
                if widget.name == current_widget_name:
                    selected_widget = widget
                    break
        selected_widget = selected_widget or server.widgets[0]

        selected_widget_html = selected_widget.render(
            language.get_lang_for_widget(selected_widget.name)
        )

        another_widgets = [
            AnotherWidget(
                widget.name,
                widget.get_method_text(language.get_lang_for_widget(widget.name)),
            )
            for widget in server.widgets
            if widget.name != selected_widget.name
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
