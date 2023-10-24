import asyncio
import logging

try:
    import twitchio
except ModuleNotFoundError:
    import subprocess
    import sys
    import os

    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "-r",
            os.path.abspath(os.path.join(os.path.dirname(__file__), "requirements.txt")),
        ]
    )

from .client import TwitchClient
from .server import LocalWebServer

logging.basicConfig(level=10)


async def main() -> None:
    queue = asyncio.Queue()

    client = TwitchClient(queue)
    server = LocalWebServer(queue, client)

    asyncio.create_task(server.start())
    await client.start()  # blocking


asyncio.run(main())
