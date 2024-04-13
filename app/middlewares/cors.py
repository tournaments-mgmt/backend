import logging

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

_logger = logging.getLogger(__name__)


def register(instance: FastAPI) -> None:
    _logger.info("Registering middleware for CORS management")

    origins: list[str] = [
        "http://localhost",
        "http://localhost:4200",
        "http://localhost:8000",
        "http://localhost:8100",
        "http://10.3.199.28",
        "http://10.3.199.28:4200",
        "http://10.3.199.28:8000",
        "http://10.3.199.28:8100",
        "http://10.3.199.112",
        "http://10.3.199.112:4200",
        "http://10.3.199.112:8000",
        "http://10.3.199.112:8100",
        "http://10.3.199.143",
        "http://10.3.199.143:4200",
        "http://10.3.199.143:8000",
        "http://10.3.199.143:8100",
    ]

    instance.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
