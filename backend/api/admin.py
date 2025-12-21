"""Admin API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from backend.auth.dependencies import require_admin
from backend.database import get_async_session
from backend.models.user import User
from backend.schemas.user import UserRead, UserCreate, UserUpdate


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=List[UserRead])
async def list_all_users(
    session: AsyncSession = Depends(get_async_session),
    admin: User = Depends(require_admin),
):
    """List all users (Admin only)."""
    result = await session.execute(select(User))
    users = result.scalars().all()
    return users


@router.get("/users/{user_id}", response_model=UserRead)
async def get_user_by_id(
    user_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    admin: User = Depends(require_admin),
):
    """Get user by ID (Admin only)."""
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    admin: User = Depends(require_admin),
):
    """Delete user by ID (Admin only)."""
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Prevent deleting self
    if user.id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account",
        )

    await session.delete(user)
    await session.commit()

    return {"message": "User deleted successfully"}


@router.get("/stats")
async def get_system_stats(
    session: AsyncSession = Depends(get_async_session),
    admin: User = Depends(require_admin),
):
    """Get system statistics (Admin only)."""
    # Count users
    result = await session.execute(select(User))
    total_users = len(result.scalars().all())

    result = await session.execute(select(User).where(User.is_admin == True))
    admin_users = len(result.scalars().all())

    return {
        "total_users": total_users,
        "admin_users": admin_users,
        "regular_users": total_users - admin_users,
    }
