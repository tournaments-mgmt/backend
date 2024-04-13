from pydantic import EmailStr, BaseModel, Field


class RegistrationFormRegisterRequestBody(BaseModel):
    nickname: str = Field(title="", description="User nickname")
    email: EmailStr = Field(title="", description="Valid e-mail address")
    tournamentName: str = Field(title="", description="Tournament name")
