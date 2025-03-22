import asyncio
import io
import logging
import shutil
import typing
from io import BytesIO
from typing import Generator
from unittest.mock import AsyncMock

import psycopg2
import pytest
from fastapi import FastAPI
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from starlette.testclient import TestClient

import tournaments_backend
from odoo.api import Environment
from tournaments_backend import persistence, instance
from tournaments_backend.config import config
from tournaments_backend.persistence.odoo_environment import OdooEnv

_logger = logging.getLogger(__name__)


class TestOdooEnv(OdooEnv):
    def __exit__(self, exc_type, exc_val, exc_tb):
        _logger.debug("Rolling back and Closing cursor")
        self._cr.rollback()
        self._cr.close()


@pytest.fixture(scope="session", autouse=True)
def config_print():
    config.print()


@pytest.fixture(scope="session")
def event_loop(request) -> typing.Generator:
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def odoo_config():
    sql_conn = psycopg2.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        user=config.DB_USERNAME,
        password=config.DB_PASSWORD,
        dbname="postgres",
    )
    sql_conn.autocommit = True
    sql_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    with sql_conn.cursor() as cr:
        cr.execute(f"DROP DATABASE IF EXISTS {config.DB_NAME}")
    sql_conn.close()

    persistence.odoo_environment.init()

    yield


@pytest.fixture
def odoo_env(odoo_config) -> Generator[Environment, None, None]:
    with OdooEnv() as env:
        yield env


@pytest.fixture
async def sync_client(odoo_config, odoo_env) -> typing.AsyncGenerator[TestClient, None]:
    db_backup_buffer = await database_backup()

    app: FastAPI = instance.app
    with TestClient(app=app) as client:
        yield client

    await database_restore(db_backup_buffer)


@pytest.fixture
def disable_showcase_worker_task():
    original = tournaments_backend.workers.showcase.ShowcaseWorker._pane_loop
    tournaments_backend.workers.showcase.ShowcaseWorker._pane_loop = AsyncMock(
        return_value=None
    )
    yield
    tournaments_backend.workers.showcase.ShowcaseWorker._pane_loop = original


@pytest.fixture
async def generate_user_testuser1(odoo_env):
    res_users_obj = odoo_env["res.users"]
    res_users = res_users_obj.create(
        {"name": "testuser1", "login": "iamatestuser1", "password": "iamatestpassword"}
    )
    if not res_users:
        raise ValueError("Unable to create test user")
    odoo_env.cr.commit()
    yield res_users


@pytest.fixture
async def generate_user_testuser2(odoo_env):
    res_users_obj = odoo_env["res.users"]
    res_users = res_users_obj.create(
        {"name": "testuser2", "login": "iamatestuser2", "password": "iamatestpassword"}
    )
    if not res_users:
        raise ValueError("Unable to create test user")
    odoo_env.cr.commit()
    yield res_users


async def database_backup() -> BytesIO:
    _logger.info("Dumping database")

    cmd: list[str] = [
        shutil.which("pg_dump"),
        f"--host={config.DB_HOST}",
        f"--port={config.DB_PORT}",
        f"--username={config.DB_USERNAME}",
        "--no-password",
        f"--dbname={config.DB_NAME}",
        "--format=c",
    ]

    env: dict = {"PGPASSWORD": config.DB_PASSWORD}

    _logger.debug(f"Running command: {' '.join(cmd)}")
    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, env=env
    )

    buffer = io.BytesIO()

    _logger.debug(f"Reading dump and saving into buffer")
    async for chunk in proc.stdout:
        buffer.write(chunk)

    await proc.wait()

    _logger.debug(f"Completed")

    buffer.seek(0)

    return buffer


async def database_restore(buffer: io.BytesIO) -> None:
    _logger.info("Restoring database")

    buffer.seek(0)

    cmd: list[str] = [
        shutil.which("pg_restore"),
        f"--host={config.DB_HOST}",
        f"--port={config.DB_PORT}",
        f"--username={config.DB_USERNAME}",
        "--no-password",
        f"--dbname={config.DB_NAME}",
        "--clean",
        "--if-exists",
        "--no-owner",
    ]

    env: dict = {"PGPASSWORD": config.DB_PASSWORD}

    _logger.debug(f"Running command: {' '.join(cmd)}")
    proc = await asyncio.create_subprocess_exec(
        *cmd, stdin=asyncio.subprocess.PIPE, env=env
    )

    _logger.debug(f"Writing dump buffer to restore command")
    while chunk := buffer.read(1024):
        proc.stdin.write(chunk)
        await proc.stdin.drain()

    proc.stdin.close()

    await proc.wait()

    _logger.debug(f"Completed")
