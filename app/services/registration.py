import logging

import psycopg2

from errors.services import CannotProceedError, AlreadyManagedError
from odoo.api import Environment

_logger = logging.getLogger(__name__)


async def register(
        odoo_env: Environment,
        nickname: str,
        email: str,
        tournament_name: str,
        x_forwarded_for: str,
        user_agent: str
) -> None:
    _logger.info("Adding registration")

    try:
        odoo_env["tournaments.registration"].create({
            "nickname": nickname,
            "email": email,
            "tournament_name": tournament_name,
            "x_forwarded_for": x_forwarded_for,
            "user_agent": user_agent
        })
    except ValueError as e:
        raise CannotProceedError(detail=str(e))
    except psycopg2.errors.UniqueViolation as e:
        raise AlreadyManagedError(detail=str(e))
