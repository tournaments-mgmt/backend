from odoo.api import Environment
from tournaments_backend.errors.backend import ServiceError


class TokenService:

    @staticmethod
    async def generate_token(user_id: int, odoo_env: Environment) -> str:
        tokens_obj = odoo_env["tournaments.token"]

        token = tokens_obj.create({"res_users_id": user_id})
        if not token:
            raise ServiceError("Token creation failed")

        return token.value
