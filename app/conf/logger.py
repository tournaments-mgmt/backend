import logging

from config import config


def init() -> None:
    logging.basicConfig(
        level=logging.WARNING,
        format=config.LOG_FORMAT,
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # logging.getLogger("PIL").setLevel(logging.WARNING)

    logging.getLogger("odoo").setLevel(config.LOG_LEVEL)
    logging.getLogger("odoo.sql_db").setLevel(logging.WARNING)

    logging.getLogger("api").setLevel(config.LOG_LEVEL)
    logging.getLogger("conf").setLevel(config.LOG_LEVEL)
    logging.getLogger("exceptions").setLevel(config.LOG_LEVEL)
    logging.getLogger("handlers").setLevel(config.LOG_LEVEL)
    logging.getLogger("middlewares").setLevel(config.LOG_LEVEL)
    logging.getLogger("models").setLevel(config.LOG_LEVEL)
    logging.getLogger("persistence").setLevel(config.LOG_LEVEL)
    logging.getLogger("services").setLevel(config.LOG_LEVEL)
    logging.getLogger("utilities").setLevel(config.LOG_LEVEL)
