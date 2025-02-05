from tinydb import Query

from ..models import Server, ProxyData
from ..connection import DatabaseConnection


class ServerDAO:
    conn: DatabaseConnection

    async def get_server_by_id(self, server_id: int) -> Server | None:
        server = await self.conn.run_command(
            self.conn.commands.get, doc_id=server_id, cond=Query().type == "server"
        )
        if isinstance(server, list):
            raise ValueError("Multiple servers found for the same id")

        if server:
            del server["type"]
            return Server(**server, id=server.doc_id)
        return None

    async def list_servers(self) -> list[Server]:
        servers = await self.conn.run_command(
            self.conn.commands.search, cond=Query().type == "server"
        )
        return [Server(**server, id=server.doc_id) for server in servers]

    async def create_server(
        self,
        name: str,
        theme_name: str,
        language: str,
        proxy_from: ProxyData,
        proxy_to: ProxyData,
    ) -> Server:
        raw = {
            "type": "server",
            "name": name,
            "theme_name": theme_name,
            "language": language,
            "proxy_from": proxy_from.model_dump(mode="json"),
            "proxy_to": proxy_to.model_dump(mode="json"),
            "widgets": [],
        }

        server_id = await self.conn.run_command(self.conn.commands.insert, raw)
        return Server(**raw, id=server_id)

    async def edit_server(self, server: Server):
        raw = server.model_dump(mode="json", exclude={"id"})
        await self.conn.run_command(
            self.conn.commands.update, fields=raw, doc_ids=[server.id]
        )
