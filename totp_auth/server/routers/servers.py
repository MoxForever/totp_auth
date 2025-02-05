from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from totp_auth.core.database import DAO, Server, ProxyData


router = APIRouter(prefix="/servers", tags=["Servers management"])


class ListServersResponse(BaseModel):
    servers: list[Server]


@router.get(
    "/list",
    summary="List all servers",
    description="Returns all servers, registered in the system",
    response_model=ListServersResponse,
    responses={200: {"description": "Successful response"}},
)
async def list_servers(request: Request) -> ListServersResponse:
    dao: DAO = request.app.state.dao
    return ListServersResponse(servers=await dao.list_servers())


class CreateServerRequest(BaseModel):
    name: str
    theme_name: str
    language: str
    proxy_from: ProxyData
    proxy_to: ProxyData


@router.post(
    "/create",
    summary="Create a new server",
    description="Creates a new server, return newly created. For futher update use "
    "[POST /servers/edit/{server_id}](#/Servers%20management/edit_server_servers_edit__server_id__post)",
    response_model=Server,
    responses={200: {"description": "Successful response"}},
)
async def create_server(request: Request, body: CreateServerRequest):
    dao: DAO = request.app.state.dao
    return await dao.create_server(
        body.name, body.theme_name, body.language, body.proxy_from, body.proxy_to
    )


class EditServerRequest(BaseModel):
    name: str | None = None
    theme_name: str | None = None
    language: str | None = None
    widgets: list[str] | None = None
    proxy_from: ProxyData | None = None
    proxy_to: ProxyData | None = None


@router.post(
    "/edit/{server_id}",
    summary="Edit server",
    description="Edit customization, widgets and language info.",
    response_model=Server,
    responses={
        200: {"description": "Successful response"},
        404: {"description": "Server not found"},
    },
)
async def edit_server(request: Request, body: EditServerRequest, server_id: int):
    dao: DAO = request.app.state.dao
    server = await dao.get_server_by_id(server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    if body.name:
        server.name = body.name
    if body.theme_name:
        server.theme_name = body.theme_name
    if body.language:
        server.language = body.language
    if body.widgets:
        server.widgets = body.widgets
    if body.proxy_from:
        server.proxy_from = body.proxy_from
    if body.proxy_to:
        server.proxy_to = body.proxy_to

    await dao.edit_server(server)

    return server
