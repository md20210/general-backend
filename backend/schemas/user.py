"""User Pydantic schemas."""
from fastapi_users import schemas
from pydantic import EmailStr
from typing import Optional
from uuid import UUID


class UserRead(schemas.BaseUser[UUID]):
    """Schema for reading user data."""
    is_admin: bool


class UserCreate(schemas.BaseUserCreate):
    """Schema for creating a new user."""
    is_admin: Optional[bool] = False


class UserUpdate(schemas.BaseUserUpdate):
    """Schema for updating user data."""
    is_admin: Optional[bool] = None
