from typing import Union

from pydantic import BaseModel, EmailStr, Field

from app.models.schemas.const import USER_ROLES


class LoginForm(BaseModel):
    username: EmailStr
    password: str


class RegisterForm(BaseModel):
    full_name: str
    email: EmailStr
    cell_phone: int
    password: str
    password_2: str
    role: Union[None, USER_ROLES] = Field(default=None)
