"""Authentication API endpoints."""
from fastapi import APIRouter, Depends
from backend.auth.dependencies import fastapi_users, current_active_user
from backend.auth.jwt import auth_backend
from backend.schemas.user import UserRead, UserCreate, UserUpdate
from backend.models.user import User


# Auth router with registration, login, logout
auth_router = APIRouter(prefix="/auth", tags=["auth"])

# Register endpoint
auth_router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
)

# Login/Logout endpoints
auth_router.include_router(
    fastapi_users.get_auth_router(auth_backend),
)

# Reset password endpoints
auth_router.include_router(
    fastapi_users.get_reset_password_router(),
)

# Verify email endpoints
auth_router.include_router(
    fastapi_users.get_verify_router(UserRead),
)

# Users management endpoints
users_router = APIRouter(prefix="/users", tags=["users"])
users_router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
)


@auth_router.get("/me", response_model=UserRead)
async def get_current_user(user: User = Depends(current_active_user)):
    """Get current authenticated user."""
    return user
