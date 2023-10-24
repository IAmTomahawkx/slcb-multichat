import asyncio
import dataclasses
import secrets
import time

import aiohttp
import twitchio
import yarl
from aiohttp import web

from . import common_types
from .client import TwitchClient
from .typings import QueueT


class LocalWebServer:
    def __init__(self, queue: QueueT, client: TwitchClient):
        self.server: web.Application = web.Application()
        self.client: TwitchClient = client
        self.queue: QueueT = queue
        self.shutdown: asyncio.Event = asyncio.Event()

        self.server.router.add_get("/updates", self.get_updates)
        self.server.router.add_get("/token", self.get_token)
        self.server.router.add_post("/shutdown", self.post_goodbye)

    async def start(self):
        await web._run_app(self.server, host="127.0.0.1", port=4835)

    async def get_updates(self, request: web.Request) -> web.Response:
        events = [self.queue.get_nowait() for _ in range(self.queue._unfinished_tasks)]
        self.queue._unfinished_tasks = 0
        self.queue._finished.set()

        formatted: list[dict] = []

        for event in events:
            if isinstance(event, twitchio.Message):
                fmt = {
                    "type": common_types.EventTypes.MESSAGE,
                    "content": event.content,
                    "author_name": event.author.display_name,
                    "author_id": event.author.id,
                    "id": event.id,
                    "tags": event.tags,
                }
            else:
                fmt = dataclasses.asdict(event)
                fmt["type"] = common_types.EventTypes.TOKEN_UPDATE

            formatted.append(fmt)

        return web.json_response(formatted)

    async def get_token_task(self, nonce: str, timeout: int = 120) -> None:
        start = time.time()
        async with aiohttp.ClientSession() as client:
            async with client.ws_connect(
                f"https://tokens.idevision.net/pickup-ws?timeout={timeout}&state={nonce}"
            ) as ws:
                remaining = (start + timeout) - time.time()
                while remaining > 0:
                    data = await ws.receive(timeout=remaining)

                    if data.type == aiohttp.WSMsgType.text:
                        body = data.json()
                        token = body["token"]
                        refresh = body["refresh"]

                        self.client.run_event("token_update", token, refresh)
                        break

                    elif data.type == aiohttp.WSMsgType.CLOSE:
                        if data.data == aiohttp.WSCloseCode.TRY_AGAIN_LATER:
                            self.client.run_event("token_timeout")

                        break
                    else:
                        remaining = (start + timeout) - time.time()

    async def get_token(self, request: web.Request) -> web.Response:
        token = request.query.get("token")
        refresh = request.query.get("refresh")
        if token and refresh:
            self.client.run_event("token_update", token, refresh)
            return web.Response(status=204)

        nonce = secrets.token_urlsafe(16)
        redirect_url = yarl.URL("https://tokens.idevision.net/redirect").with_query(
            {
                "state": nonce,
                "scopes": " ".join(["chat:read", "chat:edit", "whispers:read", "whispers:edit"]),
                "redirect": "slcb-press-reload",
            }
        )

        asyncio.create_task(self.get_token_task(nonce))

        raise web.HTTPTemporaryRedirect(str(redirect_url))

    async def post_goodbye(self, _) -> web.Response:
        self.shutdown.set()
        self.client._closing.set()
        if self.client._connection.is_alive:
            await self.client._connection._close()

        return web.Response(status=204)
