from pathlib import Path
from typing import Optional


class PageLoader:
    def __init__(self, path: str | Path):
        with open(path, "r") as f:
            self._page_raw = f.read()

    def render(self, error: Optional[str] = None):
        return self._page_raw.replace("{% ERROR %}", error or "")

    def render_response(self, error: Optional[str] = None):
        return b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n" + self.render(
            error
        ).encode("utf-8")
