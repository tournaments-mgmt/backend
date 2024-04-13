import uuid
from enum import Enum

from pydantic import EmailStr, Field

from schemas.odoo import OdooModel


class EntrantState(str, Enum):
    ENABLED = "enabled"
    BANNED = "banned"


class EntrantType(str, Enum):
    PLAYER = "player"
    TEAM = "team"


class Entrant(OdooModel):
    state: EntrantState = Field(description="Entrant state", default=EntrantState.ENABLED)
    type: EntrantType = Field(description="Entrant type", default=EntrantType.PLAYER)
    nickname: str = Field(description="Nickname")
    email: EmailStr = Field(description="E-mail")
    uuid: str | None = Field(desctiption="UUID", default=uuid.uuid4())
    avatar_color: str | None = Field(description="Player avatar color", default=None)
    age: int = Field(description="Player age")
    tournament_ids: list[int] | None = Field(description="Tournaments in which the player is entrant", default=None)
    tournament_count: int | None = Field(description="Number of tournaments", default=None)
    entrant_ids: list[int] | None = Field(description="", default=None)
    frontend_url: str | None = Field(description="Public frontend URL", default=None)
