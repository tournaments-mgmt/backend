import inspect
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html, get_swagger_ui_oauth2_redirect_html, get_redoc_html
from starlette import status
from starlette.responses import Response
from starlette.staticfiles import StaticFiles

from tournaments_backend import api, middlewares, handlers, conf, persistence
from tournaments_backend.conf.services import generate_services

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


def _register_assets(instance: FastAPI, dir_path: str) -> None:
    instance.mount("/assets", StaticFiles(directory=dir_path), name="assets")


def _register_apis(instance: FastAPI) -> None:
    for module in _get_registrable_modules(api, "router"):
        _logger.info(f"Registering API {module.__name__}")

        router_prefix: str = "/" + "/".join(module.__name__.split(".")[1:])
        _logger.debug(f"Prefix: {router_prefix}")

        instance.include_router(
            router=module.router,
            prefix=router_prefix
        )


def _register_middlewares(instance: FastAPI) -> None:
    for module in _get_registrable_modules(middlewares, "register"):
        _logger.info(f"Registering Middleware {module.__name__}")
        module.register(instance)


def _register_handlers(instance: FastAPI) -> None:
    for module in _get_registrable_modules(handlers, "register"):
        _logger.info(f"Registering Handler {module.__name__}")
        module.register(instance)


def _register_docs(instance: FastAPI) -> None:
    @instance.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        return get_swagger_ui_html(
            openapi_url=instance.openapi_url,
            title=instance.title + " - Swagger UI",
            oauth2_redirect_url=instance.swagger_ui_oauth2_redirect_url,
            swagger_js_url="/assets/swagger-ui-bundle.js",
            swagger_css_url="/assets/swagger-ui.css",
            swagger_favicon_url="/assets/favicon.png"
        )

    @instance.get(instance.swagger_ui_oauth2_redirect_url, include_in_schema=False)
    async def swagger_ui_redirect():
        return get_swagger_ui_oauth2_redirect_html()

    @instance.get("/redoc", include_in_schema=False)
    async def redoc_html():
        return get_redoc_html(
            openapi_url=instance.openapi_url,
            title=instance.title + " - ReDoc",
            redoc_js_url="/assets/redoc.standalone.js",
            redoc_favicon_url="/assets/favicon.png",
            with_google_fonts=False
        )


def _register_probes_controller(instance: FastAPI) -> None:
    async def healthz() -> Response:
        pass

    instance.add_api_route(
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


def create_instance() -> FastAPI:
    from tournaments_backend.version import APP_VERSION

    conf.logger.init()
    persistence.odoo_environment.configure()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        print(f"{app.title} {app.version}")

        async with generate_services(app):
            yield

    instance: FastAPI = FastAPI(
        title="Tournaments Management API",
        version=APP_VERSION,
        docs_url=None,
        redoc_url=None,
        openapi_url="/docs/openapi.json",
        lifespan=lifespan,
    )

    instance.openapi_version = "3.0.0"

    # _register_assets(instance, config.PATH_ASSETS)
    _register_apis(instance)
    _register_middlewares(instance)
    _register_handlers(instance)
    _register_docs(instance)
    _register_probes_controller(instance)

    return instance
