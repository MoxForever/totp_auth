from totp_auth.constants import LANGUAGES_DIRS, THEMES_DIRS, WIDGETS_DIRS
from totp_auth.database import Server
from totp_auth.renderer import PageRenderer
from totp_auth.loaders import ThemesLoader, WidgetsLoader, Translator


def test_render():
    themes_loader = ThemesLoader(THEMES_DIRS[0])
    widgets_loader = WidgetsLoader(WIDGETS_DIRS[0])
    translator = Translator(LANGUAGES_DIRS[0])
    page_renderer = PageRenderer(themes_loader, translator, widgets_loader)

    server = Server("Test server", "Dark", "en", ["totp", "password"])
    page_renderer.render_for_server(server)
