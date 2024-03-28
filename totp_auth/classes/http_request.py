from typing import AsyncGenerator


class HTTPRequest:
    def __init__(
        self, method: str, uri: str, version: str, headers: dict[str, str], body: str
    ):
        self.method = method
        self.uri = uri
        self.version = version
        self.headers = headers
        self._body = body

    def __str__(self) -> str:
        return self.to_bytes().decode("utf-8")

    @property
    def body(self):
        return self._body

    @body.setter
    def set_body(self, v):
        self.body = v
        self.headers["Content-Length"] = len(v)

    def get_cookies(self) -> dict[str, str]:
        if "Cookie" not in self.headers:
            return dict()
        else:
            return dict([i.split("=", 1) for i in self.headers["Cookie"].split("; ")])

    def to_bytes(self):
        raw = (
            f"{self.method} {self.uri} {self.version}\r\n"
            + "\r\n".join([f"{k}: {v}" for k, v in self.headers.items()])
            + "\r\n\r\n"
            + self._body
        )
        return raw.encode("utf-8")

    @staticmethod
    async def parse(data: AsyncGenerator[bytes, None]) -> "HTTPRequest":
        request_data, body, body_length, headers = None, None, 0, None

        raw = ""
        async for chunk in data:
            raw += chunk.decode("utf-8")
            if request_data is None and "\r\n" in raw:
                request_data, raw = raw.split("\r\n", 1)
            if "\r\n\r\n" in raw:
                headers, raw = raw.split("\r\n\r\n", 1)
                headers = dict([i.split(": ") for i in headers.split("\r\n")])
                body_length = int(headers.get("Content-Length", 0))
            if len(raw) >= body_length:
                body = raw
                break

        method, uri, version = request_data.split(" ")
        return HTTPRequest(
            method=method, uri=uri, version=version, headers=headers, body=body
        )
