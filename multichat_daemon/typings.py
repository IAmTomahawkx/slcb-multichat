from __future__ import annotations

import asyncio
import dataclasses

import twitchio


@dataclasses.dataclass
class TokenUpdateEvent:
    data: ValidateData
    token: str


@dataclasses.dataclass
class ValidateData:
    token: str
    refresh_token: str
    client_id: str
    login: str
    scopes: list[str]
    user_id: str
    expires_in: int


class Queue(asyncio.Queue):
    _unfinished_tasks: int
    _queue: list
    _finished: asyncio.Event


QueueT = Queue[TokenUpdateEvent | twitchio.Message]
