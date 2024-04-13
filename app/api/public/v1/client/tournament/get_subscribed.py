import logging

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from starlette import status

from odoo.api import Environment
from persistence.odoo_environment import generate_odoo_env
from services import tournaments as tournament_service

_logger = logging.getLogger(__name__)

router: APIRouter = APIRouter(
    prefix="/api/public/v1/client/tournament/get_subscribed"
)


class ResponseBody(BaseModel):
    uuid: str
    name: str
    game_name: str
    tag: str
    scheduled_start: int | None
    scheduled_end: int | None
    real_start: int | None
    real_end: int | None
    state: str


@router.get(
    path="/{entrant_uuid}",
    status_code=status.HTTP_200_OK,
    response_model=list[ResponseBody]
)
async def get_subscribed(
        entrant_uuid: str,
        odoo_env: Environment = Depends(generate_odoo_env)
) -> list[ResponseBody]:
    tournaments: list[dict] = await tournament_service.get_subscribed(odoo_env=odoo_env, entrant_uuid=entrant_uuid)
    return [ResponseBody(**tournament) for tournament in tournaments]
