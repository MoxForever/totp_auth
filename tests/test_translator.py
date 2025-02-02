from totp_auth.constants import LANGUAGES_DIRS
from totp_auth.utils.translator import Translator


def test_translator():
    translator = Translator(LANGUAGES_DIRS[0])
    assert len(translator.list_languages()) > 0


def test_get_lang():
    translator = Translator(LANGUAGES_DIRS[0])
    lang = translator.get_language("en")

    assert lang("login_page.button") == lang("login_page", "button")


def test_get_widget_lang():
    translator = Translator(LANGUAGES_DIRS[0])
    lang = translator.get_language("en")
    widget_lang = lang.get_lang_for_widget("totp")

    assert widget_lang.prekey == "auth_widgets.totp"
    assert widget_lang.name == lang.name
    assert widget_lang("login") == lang("auth_widgets.totp.login")
