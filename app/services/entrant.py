import logging

from errors.services import NotFoundError
from odoo.api import Environment
from schemas.entrant import Entrant

_logger = logging.getLogger(__name__)


async def create(odoo_env: Environment, entrant: Entrant) -> Entrant:
    _logger.info("Creating a new Entrant")

    entrant_obj = odoo_env["tournaments.entrant"]

    created_entrant = entrant_obj.create([{
        "nickname": entrant.nickname,
        "email": entrant.email,
        "age": entrant.age
    }])
    if not created_entrant:
        raise ValueError("Enable to create record")
    created_entrant = created_entrant[0]

    return Entrant.from_odoo(created_entrant)


async def read(odoo_env: Environment, domain: list[tuple] = None) -> list[Entrant]:
    _logger.info(f"Reading Entrants")

    if not domain:
        domain = list()

    return [Entrant.from_odoo(entrant) for entrant in odoo_env["tournaments.entrant"].search(domain=domain)]


async def read_team_members(odoo_env: Environment, entrant_uuid: str) -> list[Entrant]:
    _logger.info(f"Reading Entrants")

    entrant_obj = odoo_env["tournaments.entrant"]
    entrants = entrant_obj.search([
        ("type", "=", "team"),
        ("uuid", "=", entrant_uuid)
    ])
    if len(entrants) != 1:
        raise NotFoundError("unable to find team")
    team_entrant = entrants[0]

    return [Entrant.from_odoo(entrant) for entrant in team_entrant.entrant_ids]
