from tinydb import Query
from ..models import User
from ..connection import DatabaseConnection


class UserDAO:
    conn: DatabaseConnection

    async def get_user_by_id(self, user_id: int) -> User | None:
        user = await self.conn.run_command(
            self.conn.commands.get, doc_id=user_id, cond=Query().type == "user"
        )
        if isinstance(user, list):
            raise ValueError("Multiple users found for the same id")

        if user:
            del user["type"]
            return User(**user, id=user.doc_id)
        return None

    async def list_users(self) -> list[User]:
        users = await self.conn.run_command(
            self.conn.commands.search, cond=Query().type == "user"
        )
        return [User(**user, id=user.doc_id) for user in users]

    async def create_user(self, login: str) -> User:
        raw: dict = {"type": "user", "login": login}
        user_id = await self.conn.run_command(self.conn.commands.insert, raw)
        return User(**raw, id=user_id)

    async def edit_user(self, user: User):
        raw = user.model_dump(mode="json", exclude={"id"})
        await self.conn.run_command(
            self.conn.commands.update, fields=raw, doc_ids=[user.id]
        )
