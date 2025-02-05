from contextlib import asynccontextmanager

from fastapi import FastAPI

from totp_auth.core import ThemesLoader, WidgetsLoader, LanguageLoader, constants
from totp_auth.core.database import DatabaseConnection, DAO
from totp_auth.version import __version__

from .routers import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db = await DatabaseConnection.init_connection(constants.DATABASE_PATH)
    app.state.dao = DAO(app.state.db)

    app.state.themes = ThemesLoader(*constants.THEMES_DIRS)
    app.state.widgets = WidgetsLoader(*constants.WIDGETS_DIRS)
    app.state.languages = LanguageLoader(*constants.LANGUAGES_DIRS)

    yield

    app.state.db.close()


app = FastAPI(
    lifespan=lifespan,
    redoc_url=None,
    docs_url="/swagger",
    title="TOTP Auth",
    description="API of TOTP Auth service",
    version=".".join(map(str, __version__)),
)
app.include_router(router)
