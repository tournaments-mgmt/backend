from config import config
from errors.persistence import NotFoundError
from odoo.api import Environment
from odoo.exceptions import AccessDenied


async def login(odoo_env: Environment, email: str, password: str):
    try:
        return odoo_env["res.users"].authenticate(config.DB_NAME, email, password, {"interactive": False})
    except AccessDenied:
        raise NotFoundError()


async def get(odoo_env: Environment, user_id: int):
    user = odoo_env["res.users"].search([("id", "=", user_id)])
    if not user:
        raise NotFoundError("Unable to find user")
    return user
