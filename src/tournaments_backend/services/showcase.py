import asyncio
import logging

from starlette.websockets import WebSocket

import odoo
from odoo.api import Environment
from tournaments_backend.errors.showcase import (
    AlreadyManagedError,
    AlreadyConnectedError,
)
from tournaments_backend.protocol.enums import CommandType
from tournaments_backend.workers.showcase import ShowcaseWorker

_logger = logging.getLogger(__name__)


class ShowcaseService:
    _lock: asyncio.Lock

    _workers: dict[WebSocket, ShowcaseWorker]
    _tokens: list[str]

    def __init__(self) -> None:
        self._lock = asyncio.Lock()

        self._workers = dict()
        self._tokens = list()

    async def add(self, websocket: WebSocket, tag: str, odoo_env: Environment) -> None:
        async with self._lock:
            _logger.info("Adding websocket")

            if websocket in self._workers:
                raise AlreadyManagedError("Websocket already connected")

            if tag in self._tokens:
                raise AlreadyConnectedError("Token already connected")

            self._tokens.append(tag)

            showcase_obj = odoo_env["tournaments.showcase"]

            showcase = showcase_obj.search([("tag", "=", tag)])
            if not showcase:
                showcase = showcase_obj.create([{"tag": tag}])
                if not showcase:
                    raise ValueError("Unable to create record")
                showcase = showcase[0]

            showcase.write(
                {
                    "ts_last_contact": odoo.fields.Datetime.now(),
                    "last_ip_address": websocket.client
                    and websocket.client.host
                    or None,
                }
            )

            odoo_env.cr.commit()

            worker: ShowcaseWorker = ShowcaseWorker(odoo_env, websocket, showcase.id)
            self._workers[websocket] = worker
            await worker.start()

    async def remove(self, websocket: WebSocket, token: str) -> None:
        async with self._lock:
            _logger.info("Removing websocket")

            if websocket not in self._workers:
                return

            worker: ShowcaseWorker = self._workers[websocket]
            await worker.stop()
            del self._workers[websocket]

            self._tokens.remove(token)

    async def parse_message(self, websocket: WebSocket, payload: dict) -> None:
        _logger.info("Sending message to worker")

        if websocket not in self._workers:
            return

        worker: ShowcaseWorker = self._workers[websocket]
        await worker.parse_message(payload)

    @staticmethod
    def prepare_command(command_type: CommandType, data: dict | None = None) -> dict:
        command: dict = {
            "type": command_type.value,
        }

        if data is not None:
            command["data"] = data

        return command
