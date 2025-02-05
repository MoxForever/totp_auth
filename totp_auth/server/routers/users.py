from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from totp_auth.core.database import DAO, User


router = APIRouter(prefix="/users", tags=["Users managment"])


class ListUsersResponse(BaseModel):
    users: list[User]


@router.get(
    "/list",
    summary="List all users",
    description="Returns all users, registered in the system",
    response_model=ListUsersResponse,
    responses={200: {"description": "Successful response"}},
)
async def list_users(request: Request):
    dao: DAO = request.app.state.dao
    return {"users": await dao.list_users()}


class CreateUserRequest(BaseModel):
    login: str


@router.post(
    "/create",
    summary="Create a new user",
    description="Creates a new user, return newly created. For futher update use "
    "[POST /users/edit/{server_id}](#/Users%20management/edit_user_users_edit__user_id__post)",
    response_model=User,
    responses={200: {"description": "Successful response"}},
)
async def create_user(request: Request, body: CreateUserRequest):
    dao: DAO = request.app.state.dao
    return await dao.create_user(body.login)


class EditUserRequest(BaseModel):
    login: str | None = None


@router.post(
    "/edit/{user_id}",
    summary="Edit user",
    description="Edit login of user.",
    response_model=User,
    responses={
        200: {"description": "Successful response"},
        404: {"description": "User not found"},
    },
)
async def edit_user(request: Request, body: EditUserRequest, user_id: int):
    dao: DAO = request.app.state.dao
    user = await dao.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if body.login:
        user.login = body.login

    await dao.edit_user(user)
    return user
