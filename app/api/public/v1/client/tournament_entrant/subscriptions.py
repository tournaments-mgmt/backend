import logging
from services import entrant as entrant_service
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from errors.services import NotFoundError
from starlette import status
from schemas.entrant import Entrant
from schemas.tournament_entrant import TournamentEntrant
from odoo.api import Environment
from persistence.odoo_environment import generate_odoo_env
from services import tournaments as tournament_service

_logger = logging.getLogger(__name__)

router: APIRouter = APIRouter(
    prefix="/api/public/v1/client/tournament/subscriptions"
)

class TournamentEntrantResponseBody(BaseModel):
    id: int
    entrant_id: int
    uuid: str
    nickname: str
    entrant_type: str
    available: bool


@router.get(
    path="/{uuid}",
    status_code=status.HTTP_200_OK,
    response_model=list[TournamentEntrantResponseBody]
)
async def read_tournament_entrants(uuid: str, odoo_env: Environment = Depends(generate_odoo_env)) -> list[TournamentEntrantResponseBody]:
    tournament_entrants = await tournament_service.read_tournament_entrants(odoo_env=odoo_env, domain=[
        ("tournament_id.uuid", "=", uuid)
    ])

    return [TournamentEntrantResponseBody(**tournament_entrant) for tournament_entrant in tournament_entrants]


@router.put(
    path="/{tournament_entrant_id}/{available}",
    status_code=status.HTTP_200_OK,
    response_model=TournamentEntrantResponseBody
)
async def update_tournament_entrant(tournament_entrant_id: int, available: bool, odoo_env: Environment = Depends(generate_odoo_env)) -> TournamentEntrantResponseBody:
    tournament_entrant = await tournament_service.update_tournament_entrant(tournament_entrant_id=tournament_entrant_id, available=available, odoo_env=odoo_env)

    return TournamentEntrantResponseBody(**tournament_entrant)

@router.put(
    path="/byuuid/{tournament_uuid}/{entrant_uuid}/{available}",
    status_code=status.HTTP_200_OK,
    response_model=TournamentEntrantResponseBody
)
async def update_tournament_entrant(tournament_uuid: str, entrant_uuid: str, available: bool, odoo_env: Environment = Depends(generate_odoo_env)) -> TournamentEntrantResponseBody:
    tournament_entrant = await tournament_service.update_tournament_entrant_by_uuid(tournament_uuid=tournament_uuid,entrant_uuid=entrant_uuid, available=available, odoo_env=odoo_env)

    return TournamentEntrantResponseBody(**tournament_entrant)