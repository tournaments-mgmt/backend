from httpx import Response
from starlette import status

API_URL: str = "http://testserver/api/public/v1/backoffice/users/login"


async def test_login_wrong(sync_client):
    response: Response = sync_client.post(
        url=API_URL,
        json={
            "login": "",
            "password": ""
        }
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_login_existing_1(sync_client, generate_user_testuser1):
    response: Response = sync_client.post(
        url=API_URL,
        json={
            "login": "iamatestuser1",
            "password": "iamatestpassword",
        }
    )

    assert response.status_code == status.HTTP_200_OK

    response: Response = sync_client.post(
        url=API_URL,
        json={
            "login": "iamatestuser2",
            "password": "iamatestpassword",
        }
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_login_existing_2(sync_client, generate_user_testuser2):
    response: Response = sync_client.post(
        url=API_URL,
        json={
            "login": "iamatestuser1",
            "password": "iamatestpassword",
        }
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response: Response = sync_client.post(
        url=API_URL,
        json={
            "login": "iamatestuser2",
            "password": "iamatestpassword",
        }
    )

    assert response.status_code == status.HTTP_200_OK
