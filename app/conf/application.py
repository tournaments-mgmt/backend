import asyncio
import inspect
import logging
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette import status
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import Response

import api
import handlers
import middlewares
import persistence

_logger = logging.getLogger(__name__)


def _get_registrable_modules(parent_mod, component_name: str, mod_list: list = None):
    if mod_list is None:
        mod_list = list()

    for mod in [
        mod for name, mod in parent_mod.__dict__.items() if
        inspect.ismodule(mod) and mod.__name__.startswith(parent_mod.__name__)
    ]:
        _get_registrable_modules(mod, component_name, mod_list=mod_list)
        if component_name in mod.__dict__:
            mod_list.append(mod)
    return mod_list


def _register_apis(app: FastAPI) -> None:
    for module in _get_registrable_modules(api, "router"):
        _logger.info(f"Registering API {module.__name__}")

        app.include_router(module.router)


def _register_middlewares(app: FastAPI) -> None:
    for module in _get_registrable_modules(middlewares, "register"):
        _logger.info(f"Registering Middleware {module.__name__}")
        module.register(app)


def _register_handlers(app: FastAPI) -> None:
    for module in _get_registrable_modules(handlers, "register"):
        _logger.info(f"Registering Handler {module.__name__}")
        module.register(app)


def _register_probes_controller(app: FastAPI) -> None:
    async def healthz() -> Response:
        pass

    app.add_api_route(
        path="/healthz",
        methods=["GET"],
        endpoint=healthz,
        status_code=status.HTTP_204_NO_CONTENT,
        responses={
            status.HTTP_204_NO_CONTENT: {
                "description": "API working correctly"
            }
        },
        tags=["Internal Probes"]
    )


def get_instance() -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        loop = asyncio.get_running_loop()
        loop.set_default_executor(ThreadPoolExecutor(max_workers=4))

        persistence.odoo_environment.configure()

        yield

    instance = FastAPI(lifespan=lifespan)

    _register_apis(instance)
    _register_middlewares(instance)
    _register_handlers(instance)
    _register_probes_controller(instance)

    return instance
