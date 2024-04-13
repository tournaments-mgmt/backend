import logging

from errors.services import NotFoundError
from odoo.api import Environment

_logger = logging.getLogger(__name__)


async def read_entrant_related_teams(entrant_uuid: str, odoo_env: Environment):
    _logger.info(f"Reading Team of a specific Entrant")
    entrant_obj = odoo_env["tournaments.entrant"]

    entrant = entrant_obj.search(domain=[("uuid", "=", entrant_uuid)])
    teams = entrant_obj.search(domain=[("type", "=", "team"), ('entrant_ids', 'in', entrant.ids)])
    return teams
