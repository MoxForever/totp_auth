from tinydb import Query

from .models import Server
from .connection import DatabaseConnection


class DAO:
    def __init__(self, db: DatabaseConnection):
        self.conn = db

    async def get_server_by_id(self, id: int) -> Server | None:
        server = await self.conn.run_command(
            self.conn.commands.get,
            doc_id=id,
            cond=Query().type == "server",
        )
        if isinstance(server, list):
            raise ValueError("Multiple servers found for the same name")

        if server:
            del server["type"]
            return Server(**server, id=server.doc_id)
        return None

    async def create_server(self, server: Server) -> Server:
        raw = server.__dict__
        raw["type"] = "server"
        del raw["id"]

        server.id = await self.conn.run_command(self.conn.commands.insert, raw)
        return server
