import logging

import psycopg2
from schemas.entrant import Entrant
from schemas.tournament_entrant import TournamentEntrant
from errors.persistence import ORMError
from errors.services import NotFoundError, CannotProceedError
from odoo.api import Environment

_logger = logging.getLogger(__name__)


async def read(odoo_env: Environment, tournament_uuid: str = None) -> list[dict]:
    _logger.info(f"Reading Tournaments")
    tournament_obj = odoo_env["tournaments.tournament"]

    domain = list()
    if tournament_uuid is not None:
        domain.append(["uuid", "=", tournament_uuid])

    return [_render(tournament_entrant) for tournament_entrant in tournament_obj.search(domain=domain)]


async def read_all(odoo_env: Environment) -> list[dict]:
    _logger.info(f"Reading All Tournaments")
    tournament_obj = odoo_env["tournaments.tournament"]

    domain = list()

    return [_render(tournament_entrant) for tournament_entrant in tournament_obj.search(domain=domain)]


async def read_scheduled(odoo_env: Environment) -> list[dict]:
    _logger.info(f"Reading Scheduled Tournaments")
    tournament_obj = odoo_env["tournaments.tournament"]

    domain = list()
    domain.append(["state", "in", ["scheduled"]])

    return [_render(tournament_entrant) for tournament_entrant in tournament_obj.search(domain=domain)]


async def get_subscribed(odoo_env: Environment, entrant_uuid: str) -> list[dict]:
    _logger.info(f"Getting subscribed Tournaments for Entrant with UUID {entrant_uuid}")

    entrant_obj = odoo_env["tournaments.entrant"]
    tournament_entrant_obj = odoo_env["tournaments.tournament.entrant"]

    entrant = entrant_obj.search([
        ("uuid", "=", entrant_uuid)
    ])
    if not entrant:
        raise NotFoundError("Unable to fine entrant")

    tournament_entrants = tournament_entrant_obj.search([
        "|",
        "&", ("entrant_id.type", "=", "player"), ("entrant_id.uuid", "=", entrant_uuid),
        "&", ("entrant_id.type", "=", "team"), ("entrant_id.entrant_ids.uuid", "in", [entrant_uuid])
    ])

    return [_render(tournament_entrant.tournament_id) for tournament_entrant in tournament_entrants]


async def read_tournament_entrants(odoo_env: Environment, domain: list[tuple] = None) -> dict:
    _logger.info(f"Reading Entrants in a Tournament")
    tournament_entrant_obj = odoo_env["tournaments.tournament.entrant"]

    if not domain:
        domain = list()

    tournament_entrant = tournament_entrant_obj.search(domain=domain)
    if not tournament_entrant:
        raise NotFoundError("Unable to identify tournament")

    return [_render_entrant(entrant) for entrant in tournament_entrant]


# async def read_tournament_entrants(entrant_uuid: str, odoo_env: Environment, only_active: Optional[bool] = None):
#     _logger.info(f"Reading Tournament")
#
#     tournament_obj = odoo_env["tournaments.tournament"]
#     entrant_obj = odoo_env["tournaments.entrant"]
#     tz_cet = pytz.timezone('CET')
#
#     tournament_list = []
#     ids = []
#
#     entrant = entrant_obj.search(domain=[("uuid", "=", entrant_uuid)])
#     teams = await team_service.read_entrant_related_teams(entrant_uuid=entrant_uuid, odoo_env=odoo_env)
#
#     entrant_ids = [e.ids for e in entrant]
#     teams_ids = [t.ids for t in teams]
#
#     for item in entrant_ids + teams_ids:
#         ids.extend(item)
#
#     domain_entrant = []
#     domain_team = []
#
#     if only_active is not None:
#         domain_entrant.append(["state", "in", ["running", "scheduled"]])
#         domain_team.append(["state", "in", ["running", "scheduled"]])
#
#     domain_entrant.append(['entrant_ids.entrant_id', 'in', entrant.ids])
#     domain_team.append(['entrant_ids.entrant_id', 'in', teams.ids])
#
#     tournaments_entrants = tournament_obj.search(domain=domain_entrant)
#     for tournaments_entrant in tournaments_entrants:
#         tournament_list.append({"tournament_uuid": tournaments_entrant.uuid,
#                                 "entrant_uuid": entrant_uuid,
#                                 "name": tournaments_entrant.name,
#                                 "game": tournaments_entrant.game_id.tag,
#                                 "type": tournaments_entrant.entrant_type,
#                                 "state": tournaments_entrant.state,
#                                 "scheduled_start": tournaments_entrant.scheduled_start.astimezone(
#                                     tz_cet).isoformat() if tournaments_entrant.scheduled_start else None,
#                                 "real_start": tournaments_entrant.real_start.astimezone(
#                                     tz_cet).isoformat() if tournaments_entrant.real_start else None
#                                 })
#
#     tournaments_teams = tournament_obj.search(domain=domain_team)
#     for tournament_team in tournaments_teams:
#         my_teams_ids = set(tournament_team.entrant_ids.entrant_id.ids).intersection(set(teams.ids))
#         for my_team_id in my_teams_ids:
#             team = entrant_obj.search(domain=[("id", "=", my_team_id)])
#             tournament_list.append({"tournament_uuid": tournament_team.uuid,
#                                     "entrant_uuid": team.uuid,
#                                     "name": tournament_team.name,
#                                     "game": tournament_team.game_id.tag,
#                                     "type": tournament_team.entrant_type,
#                                     "state": tournament_team.state,
#                                     "scheduled_start": tournament_team.scheduled_start.astimezone(
#                                         tz_cet).isoformat() if tournament_team.scheduled_start else None,
#                                     "real_start": tournament_team.real_start.astimezone(
#                                         tz_cet).isoformat() if tournament_team.real_start else None,
#                                     "team": team.display_name})
#
#     return tournament_list

async def update_tournament_entrant(tournament_entrant_id: int, available: bool, odoo_env: Environment) -> dict:
    _logger.info(f"Setting availability of a tournament entrant with id {tournament_entrant_id}")
    tournament_entrant_obj = odoo_env["tournaments.tournament.entrant"]
    tournament_entrant = tournament_entrant_obj.browse(tournament_entrant_id)
    if not tournament_entrant:
        raise NotFoundError("Tournament Entrant not found")

    tournament_entrant.available = available

    return _render_entrant(tournament_entrant)


async def update_tournament_entrant_by_uuid(tournament_uuid: str, entrant_uuid: str, available: bool,
                                            odoo_env: Environment) -> dict:
    _logger.info(f"Setting availability to tournament uuid {tournament_uuid} of entrant with uuid {entrant_uuid}")

    tournament_obj = odoo_env["tournaments.tournament"]
    entrant_obj = odoo_env["tournaments.entrant"]
    tournament_entrant_obj = odoo_env["tournaments.tournament.entrant"]

    entrant = entrant_obj.search([
        ("uuid", "=", entrant_uuid)
    ])
    if not entrant:
        raise NotFoundError("Entrant not found")

    tournament = tournament_obj.search([("uuid", "=", tournament_uuid)])
    if not tournament:
        raise NotFoundError("Tournament not found")
    elif tournament.state == "running":
        raise CannotProceedError("Torneo in corso")
    elif tournament.state == "done":
        raise CannotProceedError("Torneo concluso")
    elif tournament.state == "canceled":
        raise CannotProceedError("Torneo annullato")

    tournament_entrant = tournament_entrant_obj.search([("tournament_id", "=", tournament.id), ("entrant_id", "=", entrant.id)])
    if not tournament_entrant:
        raise NotFoundError("Tournament Entrant not found")

    tournament_entrant.available = available

    return _render_entrant(tournament_entrant)


async def subscribe_entrant(tournament_uuid: str, entrant_uuid: str, odoo_env: Environment):
    _logger.info(f"Subscribing entrant with UUID {entrant_uuid} to Tournament with UUID {tournament_uuid}")

    tournament_obj = odoo_env["tournaments.tournament"]
    entrant_obj = odoo_env["tournaments.entrant"]
    tournament_entrant_obj = odoo_env["tournaments.tournament.entrant"]

    tournament = tournament_obj.search([("uuid", "=", tournament_uuid)])
    if not tournament:
        raise NotFoundError("Tournament not found")
    elif tournament.state == "running":
        raise CannotProceedError("Torneo in corso")
    elif tournament.state == "done":
        raise CannotProceedError("Torneo concluso")
    elif tournament.state == "canceled":
        raise CannotProceedError("Torneo annullato")

    entrant = entrant_obj.search([
        ("state", "in", ["enabled"]),
        ("uuid", "=", entrant_uuid)
    ])
    if not entrant:
        raise NotFoundError("Entrant not found")

    try:
        tournament_entrants = tournament_entrant_obj.create([{
            "tournament_id": tournament.id,
            "entrant_id": entrant.id
        }])
    except psycopg2.errors.UniqueViolation:
        raise CannotProceedError("Giocatore già iscritto")

    if len(tournament_entrants) != 1:
        raise ORMError("Unable to create Tournament Entrant")


def _render(tournament) -> dict:
    return {
        "uuid": tournament.uuid,
        "name": tournament.name,
        "game_name": tournament.game_id.name,
        "scheduled_start": tournament.scheduled_start and tournament.scheduled_start.timestamp() * 1000 or None,
        "scheduled_end": tournament.scheduled_end and tournament.scheduled_end.timestamp() * 1000 or None,
        "state": tournament.state,
    }


def _render_entrant(tournament_entrant) -> dict:
    return {
        "id": tournament_entrant.id,
        "entrant_id": tournament_entrant.entrant_id.id,
        "uuid": tournament_entrant.entrant_id.uuid,
        "nickname": tournament_entrant.entrant_nickname,
        "entrant_type": tournament_entrant.entrant_type,
        "available": tournament_entrant.available,
    }
