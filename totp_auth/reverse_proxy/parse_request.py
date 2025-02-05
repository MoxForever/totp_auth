from asyncio import StreamReader
from dataclasses import dataclass


@dataclass
class Request:
    body: str
    path: str
    method: str
    protocol: str
    headers: dict[str, str]
    raw_data: bytes


class StreamReaderHelper:
    def __init__(self, reader: StreamReader):
        self.reader = reader
        self.buffer = b""

    async def read_http_request(self) -> Request | None:
        raw_data, body = b"", b""
        method: str | None = None
        path: str | None = None
        protocol: str | None = None
        headers: dict[str, str] = dict()

        is_first_line, is_body, is_finished = True, False, False
        body_remain = 0
        while not is_finished:
            self.buffer += await self.reader.read(4096)
            if self.buffer == b"":
                return None

            sub_buffer = b""
            for b in self.buffer:
                self.buffer = self.buffer[1:]

                if is_body:
                    body += b.to_bytes(1, "big")
                    body_remain -= 1
                    if body_remain == 0:
                        is_finished = True

                else:
                    sub_buffer += b.to_bytes(1, "big")
                    if sub_buffer.endswith(b"\r\n"):
                        line = sub_buffer[:-2].decode()
                        raw_data += sub_buffer
                        sub_buffer = b""
                        if is_first_line:
                            is_first_line = False
                            method, path, protocol = line.split()
                        elif line == "":
                            is_body = True
                        else:
                            key, value = line.strip().split(": ", 1)
                            headers[key] = value
                            if key == "Content-Length":
                                body_remain = int(value)

                if body_remain == 0 and is_body:
                    is_finished = True
                    break

        if not method or not path or not protocol:
            raise ValueError("Invalid request")

        return Request(
            method=method,
            path=path,
            protocol=protocol,
            headers=headers,
            body=body.decode(),
            raw_data=raw_data,
        )
