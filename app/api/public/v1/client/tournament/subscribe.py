import logging

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from starlette import status

from odoo.api import Environment
from persistence.odoo_environment import generate_odoo_env
from services import tournaments as tournament_service

_logger = logging.getLogger(__name__)

router: APIRouter = APIRouter(
    prefix="/api/public/v1/client/tournament/subscribe"
)


class RequestBody(BaseModel):
    entrant_uuid: str
    tournament_uuid: str


@router.post(
    path="/",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def subscribe(
        request_body: RequestBody,
        odoo_env: Environment = Depends(generate_odoo_env)
) -> None:
    await tournament_service.subscribe_entrant(
        entrant_uuid=request_body.entrant_uuid,
        tournament_uuid=request_body.tournament_uuid,
        odoo_env=odoo_env
    )
