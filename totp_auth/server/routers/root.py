from typing import Literal
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from totp_auth.core.errors import LoaderError
from totp_auth.core import ThemesLoader, WidgetsLoader, LanguageLoader


router = APIRouter(prefix="", tags=["Service features"])


class ReloadResponse(BaseModel):
    status: Literal["ok"] = "ok"


@router.post(
    "/reload",
    summary="Reload customizations",
    description="Reload all custom themes, widgets and languages.",
    response_model=ReloadResponse,
    responses={
        200: {"description": "Successful response"},
        400: {
            "description": "Error in customization files",
            "content": {"application/json": {"example": {"details": "string"}}},
        },
    },
)
async def reload(request: Request):
    themes: ThemesLoader = request.app.state.themes
    widgets: WidgetsLoader = request.app.state.widgets
    languages: LanguageLoader = request.app.state.languages

    try:
        themes.reload()
        widgets.reload()
        languages.reload()
    except LoaderError as e:
        raise HTTPException(
            status_code=400, detail=f"Error during load module {e.file_path}: {e.error}"
        )

    return ReloadResponse()
