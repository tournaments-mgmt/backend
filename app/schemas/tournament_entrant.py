import uuid

from pydantic import EmailStr, Field

from schemas.odoo import OdooModel


class TournamentEntrant(OdooModel):
    id: int =  Field(description="DB Primary Key", default=None)
    entrant_nickname: str = Field(description="Nickname")
    available: bool = Field(description="Entrant Available", default=False)
    entrant_uuid: uuid.UUID = Field(description="UUID")
