import asyncio
from logging import Logger

from totp_auth.utils import get_secret_key
from totp_auth.core.database import DAO, Server
from totp_auth.core.renderer import PageRenderer

from .parse_request import StreamReaderHelper
from .response import generate_response_html


logger = Logger(__name__)


async def transmit_request(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    while True:
        request = await reader.read(1024)
        if not request:
            break

        writer.write(request)
        await writer.drain()

    writer.close()


async def proxy_request(
    server_id: int,
    dao: DAO,
    renderer: PageRenderer,
    reader_proxy: asyncio.StreamReader,
    writer_proxy: asyncio.StreamWriter,
):
    server = await dao.get_server_by_id(server_id)
    if not server:
        return

    reader_proxy_helper = StreamReaderHelper(reader_proxy)

    while True:
        request = await reader_proxy_helper.read_http_request()
        if not request:
            return

        if "Cookie" in request.headers:
            cookies = dict(
                [i.split("=", 1) for i in request.headers["Cookie"].split("; ")]
            )
            auth_token = cookies.get("totp_auth_token")
            if auth_token == "123456":
                break

        secret_key = get_secret_key()
        if not secret_key:
            raise ValueError("Secret key not found")

        writer_proxy.write(
            generate_response_html(
                401, "Unauthorized", renderer.render_for_server(server)
            )
        )
        await writer_proxy.drain()

    reader_server, writer_server = await asyncio.open_connection(
        server.proxy_to.host, server.proxy_to.port
    )
    writer_server.write(request.raw_data)
    await writer_server.drain()

    await asyncio.gather(
        transmit_request(reader_proxy, writer_server),
        transmit_request(reader_server, writer_proxy),
    )


async def serve(server: Server, dao: DAO, renderer: PageRenderer):
    proxy = await asyncio.start_server(
        lambda reader, writer: proxy_request(server.id, dao, renderer, reader, writer),
        server.proxy_from.host,
        server.proxy_from.port,
    )
    async with proxy:
        await proxy.serve_forever()
