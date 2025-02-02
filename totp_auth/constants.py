from pathlib import Path

THEMES_DIRS = [Path(__file__).parent / "static/themes", Path("/var/lib/totp_auth/themes")]
WIDGETS_DIRS = [Path(__file__).parent / "auth_widgets", Path("/var/lib/totp_auth/widgets")]
LANGUAGES_DIRS = [Path(__file__).parent / "static/langs", Path("/var/lib/totp_auth/langs")]
DATABASE_PATH = Path("/var/lib/totp_auth/totp_auth.db")
