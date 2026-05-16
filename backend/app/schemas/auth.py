"""DTO xác thực."""

from pydantic import BaseModel, Field


class LoginBody(BaseModel):
    email: str = Field(description="Email hoặc mã cheat (vd: a)")
    password: str
    remember: bool = False


class LoginResponse(BaseModel):
    token: str
    role: str
    email: str
    permissions: list[str] = []


class TokenPayload(BaseModel):
    sub: str
    role: str
    permissions: list[str] = []
