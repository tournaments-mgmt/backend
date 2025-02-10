import pydantic
from fastapi import APIRouter, Depends, Request
from starlette.status import HTTP_200_OK

from odoo.api import Environment
from tournaments_backend.persistence.odoo_environment import odoo_env_superuser
from tournaments_backend.services.authentication import AuthenticationService
from tournaments_backend.services.webtoken import WebTokenService

router: APIRouter = APIRouter()


class RequestBody(pydantic.BaseModel):
    login: str
    password: str


class ResponseBody(pydantic.BaseModel):
    token: str


@router.post(
    path="",
    response_model=ResponseBody,
    status_code=HTTP_200_OK
)
async def login(
        request: Request,
        request_body: RequestBody,
        odoo_env: Environment = Depends(odoo_env_superuser)
) -> ResponseBody:
    authentication_service: AuthenticationService = request.app.state.authentication_service
    webtoken_service: WebTokenService = request.app.state.webtoken_service

    user_id: int = await authentication_service.authenticate(request_body.login, request_body.password, odoo_env)

    data: dict = {
        "user_id": user_id
    }

    token: str = await webtoken_service.encrypt(data)

    return ResponseBody(token=token)
