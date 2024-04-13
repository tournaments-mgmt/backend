import logging
import os.path
from typing import Generator, List, Optional

from starlette.requests import Request
from starlette.websockets import WebSocket

import odoo
from config import config
from odoo.api import Environment
from odoo.modules.registry import Registry
from odoo.service.db import DatabaseExists
from odoo.sql_db import Cursor

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
        f"--without-demo=all",
        f"--init={','.join(config.ADDONS_LIST)}"
    ]

    odoo.netsvc._logger_init = True
    odoo.tools.config.parse_config(args)

    db_name: str = odoo.tools.config["db_name"]

    try:
        odoo.service.db._create_empty_database(db_name)
    except DatabaseExists:
        pass

    update_module = odoo.tools.config["init"]
    Registry.new(db_name, update_module=update_module)


def generate_odoo_env(request: Request = None, websocket: WebSocket = None) -> Generator[Environment, None, None]:
    user_id: int
    context: dict

    if request is not None:
        user_id = request.state.env_user_id
        context = request.state.env_context
    elif websocket is not None:
        user_id = getattr(websocket.state, "env_user_id", odoo.SUPERUSER_ID)
        context = getattr(websocket.state, "context", dict())
    else:
        raise ValueError("Unable to generate Odoo Env")

    with OdooEnv(user_id=user_id, context=context) as odoo_env:
        yield odoo_env


class OdooEnv:
    _user_id: int
    _context: dict

    _cr: Optional[Cursor]
    _env: Optional[Environment]

    def __init__(self, user_id: int = odoo.SUPERUSER_ID, context: dict = None):
        self._user_id = user_id

        if context is None:
            context = dict()
        self._context = context

    def __enter__(self):
        _logger.info(f"Creating Odoo Environment for user with ID {self._user_id}")

        db_name: str = odoo.tools.config["db_name"]

        registry: Registry = odoo.registry(db_name).check_signaling()
        with registry.manage_changes():
            self._cr = registry.cursor()
            self._env = Environment(self._cr, self._user_id, self._context)
            return self._env

    def __exit__(self, exc_type, exc_val, exc_tb):
        _logger.info(f"Closing Odoo Environment for user with ID {self._user_id}")

        self._env = None

        self._cr.__exit__(exc_type, exc_val, exc_tb)
        self._cr = None
