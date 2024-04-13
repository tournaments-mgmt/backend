from pydantic import EmailStr, BaseModel


class LoginRequestBody(BaseModel):
    email: str | EmailStr
    password: str


class LoginResponseBody(BaseModel):
    name: str
    jwt: str
