import logging

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from starlette import status

from odoo.api import Environment
from persistence.odoo_environment import generate_odoo_env
from services import team as team_service

_logger = logging.getLogger(__name__)

router: APIRouter = APIRouter(
    prefix="/api/public/v1/client/teams"
)


class ResponseBody(BaseModel):
    uuid: str
    name: str
    state: str


@router.get(
    path="/{entrant_uuid}",
    status_code=status.HTTP_200_OK,
    response_model=list[ResponseBody]
)
async def read(
        entrant_uuid: str,
        odoo_env: Environment = Depends(generate_odoo_env)
) -> list[dict]:
    teams = await team_service.read_entrant_related_teams(entrant_uuid, odoo_env=odoo_env)

    return [{
        "uuid": team.uuid,
        "name": team.name,
        "state": team.state
    } for team in teams]
