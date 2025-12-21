"""Authentication dependencies."""
from fastapi import Depends, HTTPException, status
from fastapi_users import FastAPIUsers
from uuid import UUID

from backend.models.user import User
from backend.auth.users import get_user_manager
from backend.auth.jwt import auth_backend


# FastAPIUsers instance
fastapi_users = FastAPIUsers[User, UUID](
    get_user_manager,
    [auth_backend],
)

# Current user dependencies
current_active_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)


async def require_admin(user: User = Depends(current_active_user)) -> User:
    """Dependency to require admin privileges."""
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return user
