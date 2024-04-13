import logging

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from starlette import status

from odoo.api import Environment
from persistence.odoo_environment import generate_odoo_env
from services import tournaments as tournament_service

_logger = logging.getLogger(__name__)

router: APIRouter = APIRouter(
    prefix="/api/public/v1/client"
)

class TournamentResponseBody(BaseModel):
    uuid: str
    name: str
    game_name: str
    scheduled_start: int | None
    scheduled_end: int | None
    state: str

@router.get(
    path="/tournaments/{tournament_uuid}",
    status_code=status.HTTP_200_OK,
    response_model=list[TournamentResponseBody]
)
async def read_tournament(
        tournament_uuid: str,
        odoo_env: Environment = Depends(generate_odoo_env)
) -> list[TournamentResponseBody]:
    tournaments: list[dict] = await tournament_service.read(odoo_env=odoo_env, tournament_uuid=tournament_uuid)
    return [TournamentResponseBody(**tournament) for tournament in tournaments]


@router.get(
    path="/tournaments",
    status_code=status.HTTP_200_OK,
    response_model=list[TournamentResponseBody]
)
async def read_all(
        odoo_env: Environment = Depends(generate_odoo_env)
) -> list[TournamentResponseBody]:
    tournaments: list[dict] = await tournament_service.read_all(odoo_env=odoo_env)
    return [TournamentResponseBody(**tournament) for tournament in tournaments]

@router.get(
    path="/tournaments_scheduled",
    status_code=status.HTTP_200_OK,
    response_model=list[TournamentResponseBody]
)
async def read_scheduled(
        odoo_env: Environment = Depends(generate_odoo_env)
) -> list[TournamentResponseBody]:
    tournaments: list[dict] = await tournament_service.read_scheduled(odoo_env=odoo_env)
    return [TournamentResponseBody(**tournament) for tournament in tournaments]