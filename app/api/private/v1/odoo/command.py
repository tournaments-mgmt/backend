import logging

from fastapi import APIRouter
from pydantic import BaseModel
from starlette import status

from protocol.enums import BroadcastMessageType
from services import showcase as showcase_service

_logger = logging.getLogger(__name__)

router: APIRouter = APIRouter(
    prefix="/api/private/v1/odoo/command"
)


class RequestModel(BaseModel):
    showcase_ids: list[int]
    message_type: BroadcastMessageType
    params: dict = dict()


@router.post(
    path="/",
    status_code=status.HTTP_204_NO_CONTENT
)
async def command(request_body: RequestModel) -> None:
    await showcase_service.broadcast_message(
        showcase_ids=request_body.showcase_ids,
        message_type=request_body.message_type,
        params=request_body.params
    )
