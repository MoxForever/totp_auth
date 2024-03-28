import asyncio

from .classes.config import Config, ServerConfig
from .classes.http_request import HTTPRequest
from .classes.page_loader import PageLoader
from .cookie import create_cookie, get_cookie_data


def redirect_answer(username: str, config: Config):
    return (
        b"HTTP/1.1 302 Found\r\nLocation: /\r\nSet-Cookie: totp_auth="
        + create_cookie(username, config).encode("utf-8")
        + b"\r\n\r\n"
    )


async def receive_request(reader):
    while True:
        yield await reader.read(4096)


async def forward_to_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    while True:
        data = await reader.read(4096)
        if not data:
            break
        writer.write(data)
        await writer.drain()


async def forward_from_client(
    reader: asyncio.StreamReader, writer: asyncio.StreamWriter, config: ServerConfig
):
    if len(config.headers_rewrite) > 0:
        while True:
            request = await HTTPRequest.parse(receive_request(reader))
            for h, v in config.headers_rewrite.items():
                request.headers[h] = v
            writer.write(request.to_bytes())
    else:
        await forward_to_client(reader, writer)


async def proxy_request(
    request: HTTPRequest,
    local_reader: asyncio.StreamReader,
    local_writer: asyncio.StreamWriter,
    config: ServerConfig,
):
    remote_reader, remote_writer = await asyncio.open_connection(*config.redirect_data)
    for h, v in config.headers_rewrite.items():
        request.headers[h] = v
    remote_writer.write(request.to_bytes())

    await asyncio.gather(
        forward_from_client(local_reader, remote_writer, config),
        forward_to_client(remote_reader, local_writer),
    )


async def handle_client(
    local_reader: asyncio.StreamReader,
    local_writer: asyncio.StreamWriter,
    server_config: ServerConfig,
    config: Config,
    page_loader: PageLoader,
):
    request = await HTTPRequest.parse(receive_request(local_reader))
    cookies = request.get_cookies()

    if get_cookie_data(cookies.get("totp_auth", ""), config) in server_config.users:
        await proxy_request(request, local_reader, local_writer, server_config)
    else:
        if request.method == "POST":
            form_data = dict([i.split("=", 1) for i in request.body.split("&")])
            username, totp = form_data.get("username").lower(), form_data.get("totp")

            correct = False
            if username in server_config.users:
                if server_config.users[username].verify(totp):
                    correct = True

            if correct:
                local_writer.write(redirect_answer(username, config))
            else:
                local_writer.write(page_loader.render_response("Incorrect data"))
        else:
            local_writer.write(page_loader.render_response())

    local_writer.close()


def handle_client_decorator(config, server_config, page_loader):
    async def handler(reader, writer):
        return await handle_client(reader, writer, server_config, config, page_loader)

    return handler


async def start_server_async(config: Config):
    page_loader = PageLoader("./totp_auth/login.html")

    servers_data = []
    for i in config.list_servers():
        await asyncio.start_server(
            handle_client_decorator(config, i, page_loader), *i.listen_data
        )

        servers_data.append(f"{i.listen} -> {i.redirect}")

    print("Server started!\n" + "\n".join(servers_data))
    await asyncio.Future()


def start_server(config: Config):
    asyncio.run(start_server_async(config))
