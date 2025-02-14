import pydantic
from fastapi import APIRouter, Depends, Request
from starlette.status import HTTP_200_OK

from odoo.api import Environment
from tournaments_backend.persistence.odoo_environment import odoo_env_superuser
from tournaments_backend.services.authentication import AuthenticationService
from tournaments_backend.services.token import TokenService

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
    token_service: TokenService = request.app.state.token_service
    user_id: int = await authentication_service.authenticate(request_body.login, request_body.password, odoo_env)
    token: str = await token_service.generate_token(user_id=user_id, odoo_env=odoo_env)
    return ResponseBody(token=token)
