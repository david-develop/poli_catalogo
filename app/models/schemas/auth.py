from typing import Union

from pydantic import BaseModel, EmailStr, Field


class LoginForm(BaseModel):
    username: EmailStr
    password: str


class RegisterForm(BaseModel):
    full_name: str
    email: EmailStr
    cell_phone: int
    password: str
    password_2: str
    role: Union[None, str] = Field(default=None)
