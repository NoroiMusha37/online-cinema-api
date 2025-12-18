from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.models.user import GenderEnum


class UserProfileBase(BaseModel):
    first_name: str = Field(max_length=32)
    last_name: str = Field(max_length=32)
    avatar: Optional[str] = None
    gender: Optional[GenderEnum] = None
    date_of_birth: Optional[date] = None
    info: Optional[str] = Field(None, max_length=512)


class UserProfileCreate(UserProfileBase):
    pass


class UserProfileUpdate(BaseModel):
    first_name: Optional[str] = Field(None, max_length=32)
    last_name: Optional[str] = Field(None, max_length=32)
    avatar: Optional[str] = None
    gender: Optional[GenderEnum] = None
    date_of_birth: Optional[date] = None
    info: Optional[str] = Field(None, max_length=512)


class UserProfileRead(UserProfileBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserRead(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    group_id: int
    profile: Optional[UserProfileRead] = None

    model_config = ConfigDict(from_attributes=True)


class UserPasswordChange(BaseModel):
    current_password: str = Field(min_length=8)
    new_password: str = Field(min_length=8)


class UserUpdateAdmin(BaseModel):
    group_id: Optional[int] = None
    is_active: Optional[bool] = None


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

    model_config = ConfigDict(from_attributes=True)


class TokenPayload(BaseModel):
    sub: int
    exp: int
    type: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    new_password: str = Field(min_length=8)
    token: str
