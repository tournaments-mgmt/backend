import asyncio
import logging
from typing import Generator
from unittest.mock import AsyncMock

import conf
import main
import persistence
import psycopg2
import pytest
import workers.showcase
from config import config
from fastapi import FastAPI
from persistence.odoo_environment import OdooEnv
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from starlette.testclient import TestClient

from odoo.api import Environment

_logger = logging.getLogger(__name__)


class TestOdooEnv(OdooEnv):

    def __exit__(self, exc_type, exc_val, exc_tb):
        _logger.debug("Rolling back and Closing cursor")
        self._cr.rollback()
        self._cr.close()


@pytest.fixture(scope="session", autouse=True)
def log_config():
    conf.logger.init()


@pytest.fixture(scope="session", autouse=True)
def config_print():
    config.config_print()


@pytest.fixture
def odoo_env(odoo_config) -> Generator[Environment, None, None]:
    with TestOdooEnv() as odoo_env:
        yield odoo_env


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()

    yield loop

    if loop.is_running():
        loop.close()


@pytest.fixture(scope="session")
def odoo_config():
    with psycopg2.connect(
            host=config.DB_HOST,
            port=config.DB_PORT,
            user=config.DB_USERNAME,
            password=config.DB_PASSWORD,
            dbname="postgres"
    ) as sql_conn:
        sql_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with sql_conn.cursor() as cr:
            cr.execute(f"DROP DATABASE IF EXISTS {config.DB_NAME}")

    persistence.odoo_environment.configure()

    yield


@pytest.fixture
def sync_client(odoo_config, odoo_env) -> TestClient:
    def generate_test_odoo_env():
        yield odoo_env

    app: FastAPI = main.app
    app.dependency_overrides[persistence.odoo_environment.generate_odoo_env] = generate_test_odoo_env

    yield TestClient(app=app)

    app.dependency_overrides = {}


@pytest.fixture
def disable_showcase_worker_task():
    original = workers.showcase.ShowcaseWorker._pane_loop
    workers.showcase.ShowcaseWorker._pane_loop = AsyncMock(return_value=None)
    yield
    workers.showcase.ShowcaseWorker._pane_loop = original
