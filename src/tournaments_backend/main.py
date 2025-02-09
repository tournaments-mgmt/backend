import asyncio
import logging
import mimetypes

import uvicorn
import uvloop

from tournaments_backend import conf

conf.logger.init()

_logger = logging.getLogger(__name__)


def main_cli() -> None:
    from tournaments_backend.config import config
    config.print()

    async def main_app() -> None:
        uvicorn_log_config = dict(uvicorn.config.LOGGING_CONFIG)
        uvicorn_log_config["formatters"]["access"]["fmt"] = config.LOG_ACCESS_FORMAT

        uvicorn.run(
            app="tournaments_backend.instance:app",
            host=config.APP_HOST,
            port=config.APP_PORT,
            workers=config.APP_WORKERS,
            log_level="info",
            log_config=uvicorn_log_config
        )

    uvloop.install()
    mimetypes.init()

    asyncio.run(main_app())
