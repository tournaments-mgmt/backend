import logging
import random
import string

from fastapi import APIRouter, WebSocket, Depends
from starlette import status
from starlette.websockets import WebSocketDisconnect, WebSocketState

from odoo.api import Environment
from tournaments_backend.errors.showcase import (
    AlreadyManagedError,
    AlreadyConnectedError,
)
from tournaments_backend.persistence.odoo_environment import odoo_env_superuser
from tournaments_backend.protocol.enums import CommandType
from tournaments_backend.services.showcase import ShowcaseService

_logger = logging.getLogger(__name__)

router: APIRouter = APIRouter()


@router.websocket(
    path="/{tag}",
)
async def ws(
    websocket: WebSocket,
    odoo_env: Environment = Depends(odoo_env_superuser),
) -> None:
    tag: str = websocket.path_params.get("tag")
    if not tag:
        await websocket.close(code=status.WS_1002_PROTOCOL_ERROR, reason="No tag")
        return

    showcase_service: ShowcaseService = websocket.app.state.showcase_service

    try:
        await showcase_service.add(websocket, tag, odoo_env)
    except AlreadyManagedError as e:
        await websocket.close(code=status.WS_1002_PROTOCOL_ERROR, reason=str(e))
        return
    except AlreadyConnectedError as e:
        new_tag: str = "".join(random.choice(string.ascii_letters) for _ in range(16))
        new_tag_data: dict = {"tag": new_tag}
        command_dict: dict = showcase_service.prepare_command(
            CommandType.NEW_TAG, new_tag_data
        )

        await websocket.accept()
        await websocket.send_json(command_dict)

        await websocket.close(code=status.WS_1002_PROTOCOL_ERROR, reason=str(e))
        return

    await websocket.accept()

    closing_reason: str = ""

    try:
        while True:
            payload = await websocket.receive_json()
            await showcase_service.parse_message(websocket, payload)
    except WebSocketDisconnect:
        _logger.info("client-side disconnection")
    except Exception as e:
        _logger.error(e)
        closing_reason = str(e)
    finally:
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.close(
                code=status.WS_1000_NORMAL_CLOSURE, reason=closing_reason
            )

        await showcase_service.remove(websocket, tag)
