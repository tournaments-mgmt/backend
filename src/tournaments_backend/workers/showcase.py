import asyncio
import logging
import traceback
from asyncio import Task

from starlette.websockets import WebSocket

import odoo
from odoo.api import Environment
from odoo.modules.registry import Registry
from tournaments_backend.protocol.enums import CommandType

_logger = logging.getLogger(__name__)


class ShowcaseWorker:
    _odoo_env: Environment
    _websocket: WebSocket
    _showcase_id: int

    _lock: asyncio.Lock

    _keep_running: bool

    _pane_task: Task | None

    def __init__(
        self, odoo_env: Environment, websocket: WebSocket, showcase_id: int
    ) -> None:
        super().__init__()

        self._odoo_env = odoo_env
        self._websocket = websocket
        self._showcase_id = showcase_id

        self._lock = asyncio.Lock()

        self._keep_running = False

        self._pane_task = None

    @property
    def showcase_id(self) -> int:
        return self._showcase_id

    async def start(self) -> None:
        async with self._lock:
            _logger.info("Starting")

            self._keep_running = True
            self._pane_task = asyncio.create_task(self._pane_loop())

    async def stop(self) -> None:
        async with self._lock:
            _logger.info("Stopping")

            self._keep_running = False
            self._pane_task.cancel()

    async def parse_message(self, payload: dict) -> None:
        async with self._lock:
            _logger.info("Parsing message")

    async def send(self, payload: dict) -> None:
        async with self._lock:
            _logger.debug("Sending payload")
            await self._websocket.send_json(payload)

    async def _pane_loop(self):
        _logger.info("Starting Pane task")

        showcase_service = self._websocket.state.showcase_service
        pane_service = self._websocket.state.pane_service

        while self._keep_running:
            duration: float

            try:
                db_name: str = odoo.tools.config["db_name"]
                registry: Registry = odoo.modules.registry.Registry(
                    db_name
                ).check_signaling()
                with registry.manage_changes():
                    with registry.cursor() as cr:
                        odoo_env: Environment = Environment(cr, odoo.SUPERUSER_ID, {})

                        pane_id: int = pane_service.get_next_showcase_pane_id(
                            odoo_env, self._showcase_id
                        )

                        pane_duration: int
                        pane_data: dict
                        pane_duration, pane_data = pane_service.get_pane_dict(
                            odoo_env, pane_id
                        )

                        duration = float(pane_duration) / 1000

                        command: dict = showcase_service.prepare_command(
                            CommandType.PANE, pane_data
                        )
                        await self._websocket.send_json(command)

            except Exception as e:
                _logger.error("Error in pane loop")
                traceback.print_exc()
                _logger.error(e)
                break

            _logger.debug(f"Sleeping {duration}")
            await asyncio.sleep(duration)
