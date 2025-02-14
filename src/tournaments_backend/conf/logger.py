import logging
import os

from tournaments_backend.config import config


class RelativePathFilter(logging.Filter):
    _app_root: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def filter(self, record):
        record.pathname = os.path.relpath(record.pathname, self._app_root)
        return True


def init():
    formatter = logging.Formatter(config.LOG_FORMAT)

    root_handler = logging.StreamHandler()
    root_handler.setLevel(logging.WARNING)
    root_handler.addFilter(RelativePathFilter())
    root_handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.setLevel(logging.WARNING)
    logger.addHandler(root_handler)

    app_handler = logging.StreamHandler()
    app_handler.setLevel(config.LOG_LEVEL)
    app_handler.addFilter(RelativePathFilter())
    app_handler.setFormatter(formatter)

    logger = logging.getLogger("tournaments_backend")
    logger.propagate = False
    logger.setLevel(config.LOG_LEVEL)
    logger.addHandler(app_handler)

    logger = logging.getLogger("conftest")
    logger.propagate = False
    logger.setLevel(config.LOG_LEVEL)
    logger.addHandler(app_handler)
