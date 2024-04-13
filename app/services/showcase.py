import asyncio
import logging
from typing import Optional

from starlette.websockets import WebSocket

import odoo
from errors.services import AlreadyManagedError, AlreadyConnectedError
from odoo.api import Environment
from protocol.enums import CommandType, BroadcastMessageType
from workers.showcase import ShowcaseWorker

_logger = logging.getLogger(__name__)

_lock: asyncio.Lock = asyncio.Lock()

workers: dict[WebSocket, ShowcaseWorker] = dict()
tokens: list[str] = list()


async def add(odoo_env: Environment, websocket: WebSocket, tag: str) -> None:
    async with _lock:
        _logger.info("Adding websocket")

        if websocket in workers:
            raise AlreadyManagedError("Websocket already connected")

        if tag in tokens:
            raise AlreadyConnectedError("Token already connected")

        tokens.append(tag)

        showcase_obj = odoo_env["tournaments.showcase"]

        showcase = showcase_obj.search([("tag", "=", tag)])
        if not showcase:
            showcase = showcase_obj.create([{"tag": tag}])
            if not showcase:
                raise ValueError("Enable to create record")
            showcase = showcase[0]

        showcase.write({
            "ts_last_contact": odoo.fields.Datetime.now(),
            "last_ip_address": websocket.client and websocket.client.host or None
        })

        odoo_env.cr.commit()

        worker: ShowcaseWorker = ShowcaseWorker(odoo_env, websocket, showcase.id)
        workers[websocket] = worker
        await worker.start()


async def remove(websocket: WebSocket, token: str) -> None:
    async with _lock:
        _logger.info("Removing websocket")

        if websocket not in workers:
            return

        worker: ShowcaseWorker = workers[websocket]
        await worker.stop()
        del workers[websocket]

        tokens.remove(token)


async def parse_message(websocket: WebSocket, payload: dict) -> None:
    _logger.info("Sending message to worker")

    if websocket not in workers:
        return

    worker: ShowcaseWorker = workers[websocket]
    await worker.parse_message(payload)


async def broadcast_message(
        showcase_ids: list[int],
        message_type: BroadcastMessageType,
        params: dict
) -> None:
    command: dict = prepare_command(CommandType.FULL_REFRESH, data=params)
    for worker in workers.values():
        if worker.showcase_id in showcase_ids:
            await worker.send(command)


def prepare_command(command_type: CommandType, data: Optional[dict] = None) -> dict:
    command: dict = {
        "type": command_type.value,
    }

    if data is not None:
        command["data"] = data

    return command
