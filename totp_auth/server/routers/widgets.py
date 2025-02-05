from fastapi import APIRouter, Request
from pydantic import BaseModel

from totp_auth.core import WidgetsLoader


router = APIRouter(prefix="/widgets", tags=["Widgets"])


class ListWidgetsResponse(BaseModel):
    widgets: list[str]


@router.get(
    "/list",
    summary="List all available widgets",
    description="List all available widgets.",
    response_model=ListWidgetsResponse,
    responses={200: {"description": "Successful response"}},
)
async def list_widgets(request: Request) -> ListWidgetsResponse:
    widgets: WidgetsLoader = request.app.state.widgets
    return ListWidgetsResponse(widgets=widgets.list_widgets())
