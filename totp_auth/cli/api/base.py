import json
from typing import Any
from http.client import HTTPConnection

from .errors import ServerDownException, InvalidRequestException
from .models import Server


class TotpHttpApi:
    def __init__(self, port: int):
        self.connection = HTTPConnection(host="localhost", port=port)

    def _request(
        self, method: str, path: str, body: str | None = None
    ) -> dict[str, Any]:
        headers = {"Content-Type": "application/json"}
        try:
            self.connection.request(method, path, body, headers)
        except ConnectionRefusedError:
            raise ServerDownException("API is not available")

        response = self.connection.getresponse()

        data = response.read()
        if 400 <= response.status <= 499:
            raise InvalidRequestException(f"API error: {data}")
        elif 500 <= response.status <= 599:
            raise ServerDownException("API returned an error")

        return json.loads(data)

    def server_list(self) -> list[Server]:
        data = self._request("GET", "/servers/list")
        return [Server(**server) for server in data["servers"]]
