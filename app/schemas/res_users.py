from pydantic import Field

from schemas.odoo import OdooModel


class ResUserModel(OdooModel):
    id: int = Field(description="DB Primary Key", default=None)
    login: str = Field(description="Value of login")
    name: str = Field(description="Name of the user")
    email: str = Field(description="E-mail address", default=None)
    partner_id: int = Field(description="Res Partner foreign key", default=None)
    groups_id: list[int] = Field(description="Groups", default=None)
