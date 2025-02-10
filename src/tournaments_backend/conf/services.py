from contextlib import asynccontextmanager

from fastapi import FastAPI

from tournaments_backend.config import config
from tournaments_backend.services.authentication import AuthenticationService
from tournaments_backend.services.webtoken import WebTokenService


@asynccontextmanager
async def generate_services(instance: FastAPI):
    instance.state.webtoken_service = WebTokenService(
        sign_key=config.JWT_SIGN_KEY.encode().decode("unicode_escape"),
        encrypt_key=config.JWT_ENCRYPT_KEY
    )

    instance.state.authentication_service = AuthenticationService()

    yield
