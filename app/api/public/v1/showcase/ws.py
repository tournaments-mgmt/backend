import logging
import random
import string

from fastapi import APIRouter, WebSocket, Depends
from starlette import status
from starlette.websockets import WebSocketDisconnect, WebSocketState

from errors.services import AlreadyManagedError, AlreadyConnectedError
from odoo.api import Environment
from persistence.odoo_environment import generate_odoo_env
from protocol.enums import CommandType
from services import showcase as showcase_service

_logger = logging.getLogger(__name__)

router: APIRouter = APIRouter(
    prefix="/api/public/v1/showcase/ws"
)


@router.websocket(
    path="/{tag}",
)
async def ws(
        websocket: WebSocket,
        odoo_env: Environment = Depends(generate_odoo_env)
) -> None:
    tag: str = websocket.path_params.get("tag")
    if not tag:
        await websocket.close(
            code=status.WS_1002_PROTOCOL_ERROR,
            reason="No tag"
        )

    try:
        await showcase_service.add(odoo_env, websocket, tag)
    except AlreadyManagedError as e:
        await websocket.close(
            code=status.WS_1002_PROTOCOL_ERROR,
            reason=str(e)
        )
        return
    except AlreadyConnectedError as e:
        new_tag: str = "".join(random.choice(string.ascii_letters) for _ in range(16))
        new_tag_data: dict = {"tag": new_tag}
        command_dict: dict = showcase_service.prepare_command(CommandType.NEW_TAG, new_tag_data)

        await websocket.accept()
        await websocket.send_json(command_dict)

        await websocket.close(
            code=status.WS_1002_PROTOCOL_ERROR,
            reason=str(e)
        )
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
                code=status.WS_1000_NORMAL_CLOSURE,
                reason=closing_reason
            )

        await showcase_service.remove(websocket, tag)
