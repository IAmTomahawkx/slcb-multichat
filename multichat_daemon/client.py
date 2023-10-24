import asyncio

import aiohttp
import twitchio
import twitchio.websocket

from .typings import ValidateData, QueueT


class TwitchClient(twitchio.Client):
    def __init__(self, dispatch_queue: QueueT):
        super().__init__(token="")
        self.queue: QueueT = dispatch_queue
        self.token_set_event: asyncio.Event = None  # type: ignore
        self.current_token_data: ValidateData | None = None

    async def reload_state(self, new_token: str, refresh: str):
        connection = self._connection
        if not connection.is_alive:
            connection._token = new_token
            if (x := await self.validate_token(new_token, refresh)) is not None:
                await self.queue.put(x)
                self._connection._initial_channels = [x.login]
                self.token_set_event.set()

            return

        self.token_set_event.clear()

        try:
            connection._keeper.cancel()
        except:
            pass

        await connection._websocket.close()
        self._connection = twitchio.websocket.WSConnection(loop=self.loop, heartbeat=30, client=self, token=new_token)

        if (x := await self.validate_token(new_token, refresh)) is not None:
            self._connection._initial_channels = [x.login]
            await self.queue.put(x)
            self.token_set_event.set()

    async def wait_for_token_unset(self):
        while self.token_set_event.is_set():  # this sucks but without making a subclassed event it'll have to do
            await asyncio.sleep(0)

    async def start(self):
        self.token_set_event: asyncio.Event = asyncio.Event()
        self._closing = asyncio.Event()

        while not self._closing.is_set():
            await asyncio.wait(
                (asyncio.create_task(self._closing.wait()), asyncio.create_task(self.token_set_event.wait())),
                return_when=asyncio.FIRST_COMPLETED,
            )

            if self._closing.is_set():
                await asyncio.sleep(0.5)
                return

            try:
                await self._connection._connect()
            except twitchio.AuthenticationError as e:
                print(e.args[0])
                self._closing.clear()  # dont close here
                self._http.session = aiohttp.ClientSession()
                self.token_set_event.clear()
                continue

            await asyncio.wait(
                (asyncio.create_task(self._closing.wait()), asyncio.create_task(self.wait_for_token_unset())),
                return_when=asyncio.FIRST_COMPLETED,
            )

        await asyncio.sleep(0.5)  # hack to get the http response out so the bot doesnt freeze

    async def event_token_update(self, new_token: str, refresh: str):  # fired ourselves
        await self.reload_state(new_token, refresh)

    async def event_message(self, message: twitchio.Message) -> None:
        await self.queue.put(message)

    async def validate_token(self, token: str, refresh: str) -> ValidateData | None:
        try:
            data = self.current_token_data = ValidateData(
                token=token, refresh_token=refresh, **(await self._http.validate(token=token))
            )
        except twitchio.AuthenticationError as e:
            print(e.args[0])
        else:
            print(data)
            return data
