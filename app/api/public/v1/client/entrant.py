import logging

from fastapi import APIRouter, Depends
from starlette import status

from errors.services import NotFoundError
from odoo.api import Environment
from persistence.odoo_environment import generate_odoo_env
from schemas.entrant import Entrant
from services import entrant as entrant_service

_logger = logging.getLogger(__name__)

router: APIRouter = APIRouter(
    prefix="/api/public/v1/client/entrant"
)


@router.get(
    path="/read/{uuid}",
    status_code=status.HTTP_200_OK,
    response_model=Entrant
)
async def read(uuid: str, odoo_env: Environment = Depends(generate_odoo_env)) -> Entrant:
    entrants = await entrant_service.read(odoo_env=odoo_env, domain=[
        ("type", "=", "player"),
        ("uuid", "=", uuid)
    ])
    if len(entrants) != 1:
        raise NotFoundError()

    return entrants[0]


@router.get(
    path="/read_team_members/{entrant_uuid}",
    status_code=status.HTTP_200_OK,
    response_model=list[Entrant]
)
async def read_team_members(entrant_uuid: str, odoo_env: Environment = Depends(generate_odoo_env)) -> list[Entrant]:
    return await entrant_service.read_team_members(odoo_env=odoo_env, entrant_uuid=entrant_uuid)


@router.post(
    path="/create",
    status_code=status.HTTP_201_CREATED,
    response_model=Entrant
)
async def create(request_body: Entrant, odoo_env: Environment = Depends(generate_odoo_env)) -> Entrant:
    return await entrant_service.create(odoo_env=odoo_env, entrant=request_body)
