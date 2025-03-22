import pytest
from starlette.websockets import WebSocketDisconnect

from tournaments_backend.protocol.enums import CommandType

WS_URL: str = f"ws://testserver/api/public/v1/showcase/ws"


def test_ws_connection_no_token(odoo_env, sync_client, disable_showcase_worker_task):
    with pytest.raises(WebSocketDisconnect):
        with sync_client.websocket_connect(url=WS_URL):
            pass

    showcase_obj = odoo_env["tournaments.showcase"]
    showcases = showcase_obj.search([])
    assert len(showcases) == 0


def test_ws_connection_with_tag(odoo_env, sync_client, disable_showcase_worker_task):
    tag: str = "token"
    url: str = f"{WS_URL}/{tag}"
    with sync_client.websocket_connect(url=url):
        showcase_obj = odoo_env["tournaments.showcase"]
        showcases = showcase_obj.search([])
        assert len(showcases) == 1

        showcase = showcases[0]
        assert showcase.tag == tag


def test_ws_connection_with_double_tag(
    odoo_env, sync_client, disable_showcase_worker_task
):
    tag: str = "token2"
    url: str = f"{WS_URL}/{tag}"

    showcase_obj = odoo_env["tournaments.showcase"]

    with sync_client.websocket_connect(url=url) as websocket_one:
        showcases = showcase_obj.search([])
        assert len(showcases) == 2

        with sync_client.websocket_connect(url=url) as websocket_two:
            response: dict = websocket_two.receive_json()
            assert "type" in response
            assert response["type"] == CommandType.NEW_TAG.value

    showcases = showcase_obj.search([])
    assert len(showcases) == 2

    showcase = showcases[1]
    assert showcase.tag == tag
