import uuid
from typing import List, Optional, TYPE_CHECKING
from datetime import date, datetime, time

from app.enums import UserRole

from pydantic import BaseModel, UUID4, ConfigDict, EmailStr, Field, field_validator


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class BaseUser(BaseSchema):
    uuid: Optional[UUID4] = None
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str 


class UserCreated(BaseSchema):
    uuid: UUID4
    username: str
    email: EmailStr
    registration_date: date
    role: UserRole

    class Config:
        orm_mode = True


class UserGet(BaseSchema):
    uuid: UUID4
    username: str
    email: EmailStr
    registration_date: date
    role: Optional[str] = None

    class Config:
        orm_mode = True


class UserChangePasswordIn(BaseModel):
    current_password: str
    new_password: str


class UserGrantPrivileges(BaseModel):
    role: UserRole

    @field_validator('role')
    def role_must_be_valid(cls, v):
        if v not in UserRole.list():
            raise ValueError(f"Invalid role. Must be one of: {UserRole.list()}")
        return v


class CredentialsSchema(BaseModel):
    email: str | None
    password: str

    class Config:
        json_schema_extra = {"example": {"email": "my_mail@email.com", "password": "qwerty"}}


class JWTToken(BaseModel):
    refresh_token: str
    access_token: str
    token_type: str


class JWTAccessToken(BaseModel):
    access_token: str
    token_type: str


class JWTRefreshToken(BaseModel):
    resresh_token: str
    token_type: str


class JWTTokenData(BaseModel):
    mail: str = None


class JWTTokenPayload(BaseModel):
    user_uuid: UUID4 = None
    token_kind: str = None


class RefreshToken(BaseModel):
    refresh_token: str


class Msg(BaseModel):
    message: str = None