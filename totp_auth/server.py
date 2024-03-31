import asyncio
import logging
from pathlib import Path
import traceback

from totp_auth.classes import AppConfig, Server, HTTPRequest, PageLoader
from totp_auth.cookie import create_cookie, get_cookie_data

logger = logging.getLogger("proxy_server")


def redirect_answer(user_id: int, config: AppConfig):
    return (
        b"HTTP/1.1 302 Found\r\nLocation: /\r\nSet-Cookie: totp_auth="
        + create_cookie(str(user_id), config).encode("utf-8")
        + b"\r\n\r\n"
    )


async def receive_request(reader: asyncio.StreamReader):
    while True:
        data = await reader.read(4096)
        if len(data) == 0:
            return
        yield data


async def forward_to_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    while True:
        data = await reader.read(4096)
        if len(data) == 0:
            return
        writer.write(data)
        await writer.drain()


async def forward_from_client(
    reader: asyncio.StreamReader, writer: asyncio.StreamWriter, server: Server
):
    try:
        if len(server.headers_rewrite) > 0:
            while True:
                request = await HTTPRequest.parse(receive_request(reader))
                if request:
                    for rewrite_header in server.headers_rewrite.values():
                        request.headers[rewrite_header.header] = rewrite_header.value
                    writer.write(request.to_bytes())
                else:
                    break
        else:
            await forward_to_client(reader, writer)
    finally:
        user_host, user_port = writer.get_extra_info("peername")
        logger.info(f"User disconnected {user_host}:{user_port}")
        return writer.close()


async def proxy_request(
    request: HTTPRequest,
    local_reader: asyncio.StreamReader,
    local_writer: asyncio.StreamWriter,
    server: Server,
):
    remote_reader, remote_writer = await asyncio.open_connection(
        server.rewrite_host, server.rewrite_port
    )
    for rewrite_header in server.headers_rewrite.values():
        request.headers[rewrite_header.header] = rewrite_header.value
    remote_writer.write(request.to_bytes())

    if request.headers.get("Upgrade") == "websocket":
        await asyncio.gather(
            forward_to_client(local_reader, remote_writer),
            forward_to_client(remote_reader, local_writer),
        )
    else:
        await asyncio.gather(
            forward_from_client(local_reader, remote_writer, server),
            forward_to_client(remote_reader, local_writer),
        )

    local_writer.close()
    remote_writer.close()
    logger.info(f"Connection closed")


async def handle_client(
    local_reader: asyncio.StreamReader,
    local_writer: asyncio.StreamWriter,
    server: Server,
    config: AppConfig,
    page_loader: PageLoader,
) -> None:
    user_host, user_port = local_writer.get_extra_info("peername")
    logger.info(f"New connection from {user_host}:{user_port}")
    request = await HTTPRequest.parse(receive_request(local_reader))
    if request is None:
        return local_writer.close()

    cookies = request.get_cookies()
    cookie_data = get_cookie_data(cookies.get("totp_auth", ""), config)
    if cookie_data and int(cookie_data) in server.users_with_access.keys():
        await proxy_request(request, local_reader, local_writer, server)
    else:
        if request.method == "POST":
            form_data = dict([i.split("=", 1) for i in request.body.split("&")])
            username, totp = form_data.get("username"), form_data.get("totp")

            user_id = None
            if username and totp:
                for i in server.users_with_access.values():
                    if username == i.username and i.totp.verify(totp):
                        user_id = i.id
                        break

            if user_id is not None:
                local_writer.write(redirect_answer(user_id, config))
            else:
                local_writer.write(page_loader.render_response("Incorrect data"))
        else:
            local_writer.write(page_loader.render_response())

    local_writer.close()
    logger.info(f"Connection ended {user_host}:{user_port}")


def handle_client_decorator(config: AppConfig, server: Server, page_loader: PageLoader):
    async def handler(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        try:
            await handle_client(reader, writer, server, config, page_loader)
        except Exception as ex:
            traceback.print_exception(ex)

    return handler


async def start_server_async(config: AppConfig) -> bool:
    page_loader = PageLoader(Path(__file__).parent / "login.html")

    servers_data = []
    for i in config.servers.values():
        await asyncio.start_server(
            handle_client_decorator(config, i, page_loader),
            i.listen_host,
            i.listen_port,
        )

        servers_data.append(f"{i.listen} -> {i.rewrite}")

    print("Server started!\n" + "\n".join(servers_data))
    await asyncio.Future()

    return True


def start_server(config: AppConfig) -> bool:
    loop = asyncio.new_event_loop()
    return loop.run_until_complete(start_server_async(config))
