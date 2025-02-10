import mimetypes

import uvicorn
import uvloop


def main_cli() -> None:
    from tournaments_backend.config import config
    config.print()

    uvloop.install()
    mimetypes.init()

    uvicorn_log_config = dict(uvicorn.config.LOGGING_CONFIG)
    uvicorn_log_config["formatters"]["access"]["fmt"] = config.LOG_ACCESS_FORMAT

    # persistence.odoo_environment.init()

    uvicorn.run(
        app="tournaments_backend.instance:app",
        host=config.APP_HOST,
        port=config.APP_PORT,
        workers=config.APP_WORKERS,
        log_level="info",
        log_config=uvicorn_log_config
    )
