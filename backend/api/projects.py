"""Project Management API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from backend.auth.dependencies import current_active_user
from backend.database import get_async_session
from backend.models.user import User
from backend.models.project import Project
from backend.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate
from backend.services.vector_store import vector_store


router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    """Create a new project."""
    project = Project(
        user_id=user.id,
        name=project_data.name,
        description=project_data.description,
        type=project_data.type,
        config=project_data.config or {},
    )

    session.add(project)
    await session.commit()
    await session.refresh(project)

    return project


@router.get("", response_model=List[ProjectRead])
async def list_projects(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    """List user's projects."""
    result = await session.execute(
        select(Project)
        .where(Project.user_id == user.id)
        .order_by(Project.updated_at.desc())
    )
    projects = result.scalars().all()
    return projects


@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(
    project_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    """Get project by ID (only if user owns it)."""
    project = await session.get(Project, project_id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    if project.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return project


@router.patch("/{project_id}", response_model=ProjectRead)
async def update_project(
    project_id: UUID,
    project_data: ProjectUpdate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    """Update project (only if user owns it)."""
    project = await session.get(Project, project_id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    if project.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Update fields
    if project_data.name is not None:
        project.name = project_data.name
    if project_data.description is not None:
        project.description = project_data.description
    if project_data.config is not None:
        project.config = project_data.config

    await session.commit()
    await session.refresh(project)

    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    """
    Delete project (only if user owns it).

    Also deletes associated vector store collection.
    """
    project = await session.get(Project, project_id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    if project.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Delete vector store collection
    try:
        vector_store.delete_collection(user.id, project_id)
    except Exception as e:
        print(f"Warning: Failed to delete vector collection: {e}")

    # Delete project (CASCADE will delete documents, chats, matches)
    await session.delete(project)
    await session.commit()

    return None
