import logging
import os.path
from typing import Generator, List, AsyncGenerator

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
        f"--load-language=en",
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


def odoo_env_superuser() -> Generator[Environment, None, None]:
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


class OdooEnv:
    _user_id: int
    _context: dict

    _cr: Cursor | None
    _env: Environment | None

    def __init__(self, user_id: int = odoo.SUPERUSER_ID, context: dict | None = None):
        self._user_id = user_id

        if context is None:
            context = dict()
        self._context = context

    def __enter__(self):
        _logger.info(f"Creating Odoo Environment for user with ID {self._user_id}")

        db_name: str = odoo.tools.config["db_name"]

        registry: Registry = odoo.modules.registry.Registry(db_name).check_signaling()
        with registry.manage_changes():
            self._cr = registry.cursor()
            self._env = Environment(self._cr, self._user_id, self._context)
            return self._env

    def __exit__(self, exc_type, exc_val, exc_tb):
        _logger.info(f"Closing Odoo Environment for user with ID {self._user_id}")

        self._env = None

        self._cr.__exit__(exc_type, exc_val, exc_tb)
        self._cr = None
