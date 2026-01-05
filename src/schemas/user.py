from datetime import datetime, date

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.models.user import GenderEnum


class UserProfileBase(BaseModel):
    first_name: str = Field(max_length=32)
    last_name: str = Field(max_length=32)
    avatar: str | None = None
    gender: GenderEnum | None = None
    date_of_birth: date | None = None
    info: str | None = Field(None, max_length=512)


class UserProfileCreate(UserProfileBase):
    pass


class UserProfileUpdate(BaseModel):
    first_name: str | None = Field(None, max_length=32)
    last_name: str | None = Field(None, max_length=32)
    avatar: str | None = None
    gender: GenderEnum | None = None
    date_of_birth: date | None = None
    info: str | None = Field(None, max_length=512)


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
    profile: UserProfileRead | None = None

    model_config = ConfigDict(from_attributes=True)


class UserPasswordChange(BaseModel):
    current_password: str = Field(min_length=8)
    new_password: str = Field(min_length=8)


class UserUpdateAdmin(BaseModel):
    group_id: int | None = None
    is_active: bool | None = None


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
