from fastapi import APIRouter, Depends
from starlette import status

from odoo.api import Environment
from persistence.odoo_environment import generate_odoo_env
from schemas.auth import LoginResponseBody, LoginRequestBody
from services import jwt as jwt_service
from services import user as user_service

router: APIRouter = APIRouter(prefix="/api/public/v1/registration/auth")


@router.post(
    path="/login",
    status_code=status.HTTP_200_OK,
    response_model=LoginResponseBody
)
async def login(
        request_body: LoginRequestBody,
        odoo_env: Environment = Depends(generate_odoo_env)
) -> LoginResponseBody:
    user_id: int = await user_service.login(odoo_env=odoo_env, email=request_body.email, password=request_body.password)
    user = await user_service.get(odoo_env=odoo_env, user_id=user_id)
    jwt: str = jwt_service.generate(user_id=user.id)
    return LoginResponseBody(name=user.name, jwt=jwt)


@router.post(
    path="/validate",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None
)
async def validate(odoo_env: Environment = Depends(generate_odoo_env)) -> None:
    pass
