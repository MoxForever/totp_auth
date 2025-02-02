from totp_auth.auth_widgets import TOTPWidget, PasswordWidget
from totp_auth.constants import LANGUAGES_DIRS, THEMES_DIRS
from totp_auth.database import Server
from totp_auth.renderer import PageRenderer
from totp_auth.utils.load_themes import ThemesLoader
from totp_auth.utils.translator import Translator


def test_render():
    themes_loader = ThemesLoader(THEMES_DIRS[0])
    translator = Translator(LANGUAGES_DIRS[0])
    page_renderer = PageRenderer(themes_loader, translator)

    widget = TOTPWidget()
    server = Server("Test server", "Dark", "en", [widget, PasswordWidget()])

    page_renderer.render_for_server(server)
