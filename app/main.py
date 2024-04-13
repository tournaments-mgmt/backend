import uvicorn
import uvloop
from fastapi import FastAPI

import conf
from config import config
from app_version import print_app_version

uvloop.install()
app: FastAPI = conf.application.get_instance()

if __name__ == "__main__":
    conf.logger.init()

    config.config_print()
    print_app_version()

    uvicorn_log_config = dict(uvicorn.config.LOGGING_CONFIG)
    uvicorn_log_config["formatters"]["access"]["fmt"] = config.LOG_ACCESS_FORMAT

    uvicorn.run(
        app="main:app",
        host=config.HTTP_HOST,
        port=config.HTTP_PORT,
        workers=config.APP_WORKERS,
        log_level="info",
        log_config=uvicorn_log_config
    )
