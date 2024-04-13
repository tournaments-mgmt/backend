import logging

from fastapi import APIRouter, Depends
from starlette import status
from starlette.requests import Request

from odoo.api import Environment
from persistence.odoo_environment import generate_odoo_env
from schemas.registration import RegistrationFormRegisterRequestBody
from services import registration as registration_service

_logger = logging.getLogger(__name__)

router: APIRouter = APIRouter(
    prefix="/api/public/v1/registration/form",
    tags=["Registration"]
)


@router.post(
    path="/register",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    responses={
        status.HTTP_406_NOT_ACCEPTABLE: {"description": "Invalid values in the request (e.g. not existing tournament)"},
        status.HTTP_409_CONFLICT: {"description": "Already registered"},
    }
)
async def register(
        request_body: RegistrationFormRegisterRequestBody,
        request: Request,
        odoo_env: Environment = Depends(generate_odoo_env)
) -> None:
    x_forwarded_for: str = request.headers.get("X-Forwarded-For", "")
    user_agent: str = request.headers.get("User-Agent", "")
    _logger.debug(f"Register called from \"{x_forwarded_for}\" using \"{user_agent}\"")

    await registration_service.register(
        odoo_env=odoo_env,
        nickname=request_body.nickname,
        email=request_body.email,
        tournament_name=request_body.tournamentName,
        x_forwarded_for=x_forwarded_for,
        user_agent=user_agent,
    )
