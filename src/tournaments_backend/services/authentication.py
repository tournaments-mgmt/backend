import logging
import traceback

import odoo
from odoo.api import Environment
from tournaments_backend.errors.services import AuthenticationError

_logger = logging.getLogger(__name__)


class AuthenticationService:
    @staticmethod
    async def authenticate(login: str, password: str, odoo_env: Environment) -> int:
        if not login or not password:
            _logger.error("Invalid login or password")
            raise AuthenticationError()

        kwargs: dict = {
            "db": odoo.tools.config["db_name"],
            "credential": {"type": "password", "login": login, "password": password},
            "user_agent_env": {"interactive": False},
        }

        try:
            auth_info = odoo_env["res.users"].authenticate(**kwargs)
        except Exception as e:
            _logger.error(f"Authentication failed: {e}\n{traceback.format_exc()}")
            raise AuthenticationError()

        return auth_info["uid"]
