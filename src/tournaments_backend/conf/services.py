import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from tournaments_backend.config import config
from tournaments_backend.services.authentication import AuthenticationService
from tournaments_backend.services.token import TokenService
from tournaments_backend.services.webtoken import WebTokenService

_logger = logging.getLogger(__name__)


@asynccontextmanager
async def generate_services(instance: FastAPI):
    _logger.info("Generating services")

    _logger.debug("Generating WebTokenService")
    instance.state.webtoken_service = WebTokenService(
        sign_key=config.JWT_SIGN_KEY.encode().decode("unicode_escape"),
        encrypt_key=config.JWT_ENCRYPT_KEY,
    )

    _logger.debug("Generating AuthenticationService")
    instance.state.authentication_service = AuthenticationService()

    _logger.debug("Generating TokenService")
    instance.state.token_service = TokenService()

    yield
