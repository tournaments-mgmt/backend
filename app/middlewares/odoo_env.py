import logging

from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

import odoo

_logger = logging.getLogger(__name__)

ROUTES_ALLOWED = ["/docs", "/openapi.json", "/healthz", "/redoc"]


class OdooEnvironmentMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request.state.env_user_id = odoo.SUPERUSER_ID
        request.state.env_context = dict()

        return await call_next(request)


def register(instance: FastAPI) -> None:
    instance.add_middleware(OdooEnvironmentMiddleware)
