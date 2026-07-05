from sqlmodel import SQLModel, Field
from datetime import datetime, timezone


class UserBase(SQLModel):
    email: str = Field(unique=True)
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    password: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserUpdate(SQLModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=50)
    last_name: str | None = Field(default=None, min_length=1, max_length=50)


class UserPasswordUpdate(SQLModel):
    current_password: str = Field(min_length=8)
    new_password: str = Field(min_length=8)


class UserPublic(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime


class AuthResponse(SQLModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic
