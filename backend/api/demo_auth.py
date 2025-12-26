"""Demo authentication endpoint for testing without login."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.database import get_async_session
from backend.models.user import User
from backend.auth.users import get_user_manager, UserManager

router = APIRouter(prefix="/demo", tags=["Demo"])


@router.get("/token")
async def get_demo_token(
    db: AsyncSession = Depends(get_async_session),
    user_manager: UserManager = Depends(get_user_manager)
):
    """
    Get JWT token for demo user (testing only).

    Creates demo user if not exists, returns valid JWT token.

    WARNING: This endpoint should be DISABLED in production!
    """
    demo_email = "demo@lifechonicle.app"
    demo_password = "demo123"

    # Check if demo user exists
    result = await db.execute(
        select(User).where(User.email == demo_email)
    )
    demo_user = result.scalar_one_or_none()

    # Create demo user if not exists
    if not demo_user:
        from backend.schemas.user import UserCreate
        user_create = UserCreate(
            email=demo_email,
            password=demo_password,
            is_verified=True
        )
        demo_user = await user_manager.create(user_create)

    # Generate JWT token
    from backend.auth.backend import auth_backend
    from fastapi_users.authentication import Strategy

    strategy: Strategy = auth_backend.get_strategy()
    token = await strategy.write_token(demo_user)

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": str(demo_user.id),
            "email": demo_user.email
        }
    }
