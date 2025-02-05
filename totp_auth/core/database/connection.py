import asyncio
from pathlib import Path
from typing import Callable, TypeVar, ParamSpec
from concurrent.futures import ThreadPoolExecutor

from tinydb import TinyDB


T = TypeVar("T", covariant=True)
P = ParamSpec("Params")
RunResult = TypeVar("RunResult")


class DatabaseConnection:
    def __init__(
        self, loop: asyncio.AbstractEventLoop, pool: ThreadPoolExecutor, db: TinyDB
    ):
        self.loop = loop
        self.pool = pool
        self.commands = db

    def close(self):
        self.commands.close()
        self.pool.shutdown()

    @staticmethod
    async def init_connection(path: Path) -> "DatabaseConnection":
        loop = asyncio.get_event_loop()
        pool = ThreadPoolExecutor(max_workers=1)
        db = await loop.run_in_executor(pool, TinyDB, path)
        return DatabaseConnection(loop, pool, db)

    async def run_command(
        self, command: Callable[P, T], *args: P.args, **kwargs: P.kwargs
    ) -> T:
        def run_func():
            return command(*args, **kwargs)

        return await self.loop.run_in_executor(self.pool, run_func)
