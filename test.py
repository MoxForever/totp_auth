from totp_auth.reverse_proxy.main import serve

from totp_auth.core import ThemesLoader, WidgetsLoader, LanguageLoader, constants
from totp_auth.core.database import DatabaseConnection, DAO
from totp_auth.core.renderer import PageRenderer


async def main():
    dao_connections = DatabaseConnection.init_connection(constants.DATABASE_PATH)
    dao = DAO(await dao_connections)

    themes = ThemesLoader(*constants.THEMES_DIRS)
    widgets = WidgetsLoader(*constants.WIDGETS_DIRS)
    languages = LanguageLoader(*constants.LANGUAGES_DIRS)

    renderer = PageRenderer(
        themes_loader=themes, translator=languages, widgets_loader=widgets
    )

    server = await dao.get_server_by_id(1)
    if not server:
        raise ValueError("Server not found")

    await serve(server, dao, renderer)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
