from fastapi import APIRouter, Depends
from starlette.status import HTTP_204_NO_CONTENT

from odoo.api import Environment
from tournaments_backend.persistence.odoo_environment import odoo_env_web_token

router: APIRouter = APIRouter()


@router.get(
    path="",
    status_code=HTTP_204_NO_CONTENT
)
async def validate(odoo_env: Environment = Depends(odoo_env_web_token)) -> None:
    return
