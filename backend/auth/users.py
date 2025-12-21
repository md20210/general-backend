"""User manager and database dependencies."""
from typing import Optional
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, UUIDIDMixin
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from backend.config import settings
from backend.database import get_async_session
from backend.models.user import User
from backend.auth.password import BcryptPasswordHelper


class UserManager(UUIDIDMixin, BaseUserManager[User, UUID]):
    """User manager for fastapi-users."""

    reset_password_token_secret = settings.SECRET_KEY
    verification_token_secret = settings.SECRET_KEY

    def __init__(self, user_db: SQLAlchemyUserDatabase):
        """Initialize user manager with custom password helper."""
        # MUST call super().__init__ FIRST
        super().__init__(user_db)

    @property
    def password_helper(self):
        """Override password helper to use bcrypt directly."""
        if not hasattr(self, '_password_helper'):
            self._password_helper = BcryptPasswordHelper(rounds=12)
        return self._password_helper

    @password_helper.setter
    def password_helper(self, value):
        """Ignore any attempts to set password_helper from parent class."""
        # Just store it but we'll override it in the getter
        self._password_helper = BcryptPasswordHelper(rounds=12)

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        """Called after user registration."""
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        """Called after forgot password request."""
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        """Called after verification request."""
        print(f"Verification requested for user {user.id}. Verification token: {token}")


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    """Get user database instance."""
    yield SQLAlchemyUserDatabase(session, User)


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    """Get user manager instance."""
    yield UserManager(user_db)
