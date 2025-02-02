from pathlib import Path

THEMES_DIRS = [Path(__file__).parent / "static/themes", "/var/lib/totp_auth/themes"]
WIDGETS_DIRS = [Path(__file__).parent / "widgets", "/var/lib/totp_auth/widgets"]
LANGUAGES_DIRS = [Path(__file__).parent / "static/langs", "/var/lib/totp_auth/langs"]
