import logging
import os.path
from typing import List, AsyncGenerator

from fastapi import Request, WebSocket

import odoo
from odoo.api import Environment
from odoo.modules.registry import Registry
from odoo.service.db import DatabaseExists
from odoo.sql_db import Cursor
from tournaments_backend.config import config
from tournaments_backend.errors.backend import AuthorizationError
from tournaments_backend.services.webtoken import WebTokenService

_logger = logging.getLogger(__name__)


def configure() -> None:
    _logger.info("Configuring Odoo")

    addons_path: str = ",".join(list(map(lambda x: os.path.abspath(x), config.ADDONS_PATH)))
    data_dir: str = os.path.abspath(config.DATADIR)

    args: List[str] = [
        f"--addons-path={addons_path}",
        f"--data-dir={data_dir}",
        f"--db_host={config.DB_HOST}",
        f"--db_port={config.DB_PORT}",
        f"--db_user={config.DB_USERNAME}",
        f"--db_password={config.DB_PASSWORD}",
        f"--database={config.DB_NAME}",
        # f"--load-language=en",
        f"--without-demo=all",
        f"--init={','.join(config.ADDONS_LIST)}"
    ]

    odoo.netsvc._logger_init = True
    odoo.tools.config.parse_config(args)


def init() -> None:
    _logger.info("Initializing Odoo")

    configure()

    db_name: str = odoo.tools.config["db_name"]

    try:
        odoo.service.db._create_empty_database(db_name)
    except DatabaseExists:
        pass

    update_module = odoo.tools.config["init"]
    Registry.new(db_name, update_module=update_module)


async def odoo_env_superuser() -> AsyncGenerator[Environment, None]:
    user_id: int = odoo.SUPERUSER_ID
    context: dict = dict()

    with OdooEnv(user_id=user_id, context=context) as odoo_env:
        yield odoo_env


async def odoo_env_web_token(request: Request = None, websocket: WebSocket = None) -> AsyncGenerator[Environment, None]:
    if request is not None:
        authorization_header: str | None = request.headers.get("Authorization", None)
        if not authorization_header:
            raise AuthorizationError()

    elif websocket is not None:
        authorization_header: str | None = websocket.headers.get("Authorization", None)
        if not authorization_header:
            raise AuthorizationError()

    else:
        raise ValueError("Unable to generate Odoo Env")

    header_items = authorization_header.split(" ")
    if len(header_items) != 2:
        raise AuthorizationError()

    encrypted_data: str = header_items[1]

    webtoken_service: WebTokenService = request.app.state.webtoken_service
    data: dict = await webtoken_service.decrypt(encrypted_data=encrypted_data)

    if "user_id" not in data:
        raise AuthorizationError()

    user_id: int = data.get("user_id")
    context: dict = data.get("context", dict())

    with OdooEnv(user_id=user_id, context=context) as odoo_env:
        yield odoo_env


async def odoo_env_token(request: Request = None, websocket: WebSocket = None) -> AsyncGenerator[Environment, None]:
    if request is not None:
        authorization_header: str | None = request.headers.get("Authorization", None)
        if not authorization_header:
            raise AuthorizationError()

    elif websocket is not None:
        authorization_header: str | None = websocket.headers.get("Authorization", None)
        if not authorization_header:
            raise AuthorizationError()

    else:
        raise ValueError("Unable to generate Odoo Env")

    header_items = authorization_header.split(" ")
    if len(header_items) != 2:
        raise AuthorizationError()

    token_value: str = header_items[1]

    with OdooEnv() as env:
        token_obj = env["tournaments.token"]
        token = token_obj.search([("value", "=", token_value)], limit=1)
        if not token:
            raise AuthorizationError()
        user_id: int = token.res_users_id.id

    with OdooEnv(user_id=user_id) as env:
        yield env


class OdooEnv:
    _user_id: int
    _context: dict

    _registry: Registry | None
    _cr: Cursor | None
    _env: Environment | None

    _test_mode: bool

    def __init__(
            self,
            user_id: int = odoo.SUPERUSER_ID,
            context: dict | None = None,
            cr: Cursor | None = None,
            test_mode: bool = False
    ):
        self._user_id = user_id

        if context is None:
            context = dict()
        self._context = context

        self._cr = cr

        self._test_mode = test_mode

    def __enter__(self):
        _logger.info(f"Creating Odoo Environment for user with ID {self._user_id}")

        db_name: str = odoo.tools.config["db_name"]

        self._registry: Registry = odoo.modules.registry.Registry(db_name).check_signaling()
        if self._registry.in_test_mode():
            _logger.info(f"Odoo Env already in test mode")

        with self._registry.manage_changes():
            if self._cr is None:
                _logger.debug("Creating cursor")
                self._cr = self._registry.cursor()

            if self._test_mode:
                _logger.debug("Entering in test mode")
                self._registry.enter_test_mode(self._cr, test_readonly_enabled=False)

            self._env = Environment(self._cr, self._user_id, self._context)
            return self._env

    def __exit__(self, exc_type, exc_val, exc_tb):
        _logger.info(f"Closing Odoo Environment for user with ID {self._user_id}")

        self._env = None
        if self._test_mode:
            _logger.debug("Leaving test mode")
            self._registry.leave_test_mode()

        self._cr.__exit__(exc_type, exc_val, exc_tb)
        self._cr = None
