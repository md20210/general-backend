"""User Pydantic schemas."""
from fastapi_users import schemas
from pydantic import EmailStr
from typing import Optional
from uuid import UUID


class UserRead(schemas.BaseUser[UUID]):
    """Schema for reading user data."""
    is_admin: bool
    vorname: Optional[str] = None
    nachname: Optional[str] = None
    sprache: str = "de"
    telefonnummer: Optional[str] = None


class UserCreate(schemas.BaseUserCreate):
    """Schema for creating a new user."""
    is_admin: Optional[bool] = False
    vorname: Optional[str] = None
    nachname: Optional[str] = None
    sprache: str = "de"
    telefonnummer: Optional[str] = None


class UserUpdate(schemas.BaseUserUpdate):
    """Schema for updating user data."""
    is_admin: Optional[bool] = None
    vorname: Optional[str] = None
    nachname: Optional[str] = None
    sprache: Optional[str] = None
    telefonnummer: Optional[str] = None
