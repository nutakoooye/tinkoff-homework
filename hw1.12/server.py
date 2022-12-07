import asyncio
import aiofiles
import socket
from aiohttp import web
from aiohttp import ClientSession
from pathlib import Path

NOT_FOUND_TEXT = "<h1>404 - File not found</h1>"


class ServerURL:
    def __init__(
        self, port: int, path: str, neighbors: dict, save_copies: bool
    ):
        self.__port = port
        self.__path = Path(path)
        self.__neighbors = neighbors
        self.__save_copies = save_copies

    @staticmethod
    async def __load_file(path_to_file: Path) -> str:
        async with aiofiles.open(path_to_file, "r", encoding="UTF8") as file:
            return await file.read()

    @staticmethod
    async def __save_file(path_to_file: Path, content) -> None:
        async with aiofiles.open(path_to_file, "x", encoding="UTF8") as file:
            await file.write(content)

    async def __save_file_copy(self, filename: str, content: str):
        if self.__save_copies:
            path = Path(self.__path, filename)
            await self.__save_file(path, content)

    @staticmethod
    async def __poll_one_daemon(
        host: str, port: int, filename: str
    ) -> str | None:

        headers = {'is_daemon_client': "yes"}
        async with ClientSession(headers=headers) as session:
            url = f'http://{host}:{port}/{filename}'

            async with session.get(url) as response:
                if response.status == 200:
                    return await response.text()
                return None

    @staticmethod
    def __daemon_is_work(host: str, port: int) -> bool:
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            conn.connect((host, port))
        except ConnectionRefusedError:
            return False
        finally:
            conn.close()
        return True

    async def __poll_all_daemons(self, filename: str) -> list[str | None]:
        tasks = []
        for daemon in self.__neighbors.values():
            host, port = daemon["host"], daemon["port"]
            if self.__daemon_is_work(host, port):
                tasks.append(
                    asyncio.create_task(
                        self.__poll_one_daemon(host, port, filename)
                    )
                )

        results = await asyncio.gather(*tasks)
        return results

    async def __run_daemons_polling(self, filename: str) -> web.Response:
        results = await self.__poll_all_daemons(filename)
        for res in results:
            if res:
                await self.__save_file_copy(filename, res)
                return web.Response(text=res, content_type="text/html")
        raise web.HTTPNotFound(text=NOT_FOUND_TEXT, content_type="text/html")

    async def __handle(self, request: web.Request) -> web.Response:
        filename = request.match_info["filename"]
        path_to_file = Path(self.__path, filename)

        if path_to_file.is_file():
            text = await self.__load_file(path_to_file)
            return web.Response(text=text, content_type="text/html")

        if "is_daemon_client" not in request.headers:
            return await self.__run_daemons_polling(filename)

        raise web.HTTPNotFound(text=NOT_FOUND_TEXT, content_type="text/html")

    async def __main(self):
        app = web.Application()
        app.add_routes([web.get(r'/{filename}', self.__handle)])

        runner = web.AppRunner(app)

        await runner.setup()
        site = web.TCPSite(runner, 'localhost', self.__port)
        await site.start()

        while True:
            await asyncio.sleep(3600)

    def run(self):
        asyncio.run(self.__main())
