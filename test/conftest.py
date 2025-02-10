import asyncio
import typing

import pytest

from tournaments_backend.services.webtoken import WebTokenService


@pytest.fixture(scope="session")
def event_loop(request) -> typing.Generator:
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def webtoken_service():
    yield WebTokenService(
        sign_key="-----BEGIN PRIVATE KEY-----\nMC4CAQAwBQYDK2VwBCIEIBgL/kfqHKHq9nkUYtfmj7lFQ+OUb+ymd4VbzYUse4Ef\n-----END PRIVATE KEY-----\n",
        encrypt_key="SXkFiTqwekNLvITKukrZ4sp3psTjpVkDyelHBOeSF2M="
    )
