import logging

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

_logger = logging.getLogger(__name__)


def register(instance: FastAPI) -> None:
    _logger.info("Registering middleware for CORS management")

    instance.add_middleware(
        CORSMiddleware,
        allow_origin_regex=".*",
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "PUT"],
        allow_headers=["*"]
    )
