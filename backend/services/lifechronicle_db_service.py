"""LifeChronicle Service with PostgreSQL database backend."""
from typing import List, Optional
from uuid import UUID
from datetime import date
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.lifechronicle import LifeChronicleEntry
from backend.schemas.lifechronicle import (
    LifeChronicleEntryCreate,
    LifeChronicleEntryUpdate,
)


class LifeChronicleDBService:
    """Database service for LifeChronicle entries."""

    async def get_all_entries(
        self,
        db: AsyncSession,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[LifeChronicleEntry]:
        """
        Get all timeline entries for a user, sorted by date (newest first).

        Args:
            db: Database session
            user_id: User ID for filtering
            skip: Number of entries to skip (pagination)
            limit: Maximum number of entries to return

        Returns:
            List of LifeChronicleEntry objects
        """
        result = await db.execute(
            select(LifeChronicleEntry)
            .where(LifeChronicleEntry.user_id == user_id)
            .order_by(LifeChronicleEntry.date.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_entry(
        self,
        db: AsyncSession,
        entry_id: UUID,
        user_id: UUID
    ) -> Optional[LifeChronicleEntry]:
        """
        Get a single entry by ID (user-scoped).

        Args:
            db: Database session
            entry_id: Entry ID
            user_id: User ID for authorization

        Returns:
            LifeChronicleEntry or None if not found/unauthorized
        """
        result = await db.execute(
            select(LifeChronicleEntry)
            .where(
                LifeChronicleEntry.id == entry_id,
                LifeChronicleEntry.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def create_entry(
        self,
        db: AsyncSession,
        user_id: UUID,
        entry_data: LifeChronicleEntryCreate
    ) -> LifeChronicleEntry:
        """
        Create a new timeline entry.

        Args:
            db: Database session
            user_id: User ID
            entry_data: Entry creation data

        Returns:
            Created LifeChronicleEntry
        """
        entry = LifeChronicleEntry(
            user_id=user_id,
            title=entry_data.title,
            date=entry_data.date,
            original_text=entry_data.original_text,
            is_refined=False
        )
        db.add(entry)
        await db.commit()
        await db.refresh(entry)
        return entry

    async def update_entry(
        self,
        db: AsyncSession,
        entry_id: UUID,
        user_id: UUID,
        entry_data: LifeChronicleEntryUpdate
    ) -> Optional[LifeChronicleEntry]:
        """
        Update an existing entry.

        Args:
            db: Database session
            entry_id: Entry ID
            user_id: User ID for authorization
            entry_data: Update data

        Returns:
            Updated entry or None if not found/unauthorized
        """
        entry = await self.get_entry(db, entry_id, user_id)
        if not entry:
            return None

        # Update only provided fields
        update_dict = entry_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(entry, field, value)

        await db.commit()
        await db.refresh(entry)
        return entry

    async def delete_entry(
        self,
        db: AsyncSession,
        entry_id: UUID,
        user_id: UUID
    ) -> bool:
        """
        Delete an entry.

        Args:
            db: Database session
            entry_id: Entry ID
            user_id: User ID for authorization

        Returns:
            True if deleted, False if not found/unauthorized
        """
        entry = await self.get_entry(db, entry_id, user_id)
        if not entry:
            return False

        await db.delete(entry)
        await db.commit()
        return True

    async def mark_as_refined(
        self,
        db: AsyncSession,
        entry_id: UUID,
        user_id: UUID,
        refined_text: str
    ) -> Optional[LifeChronicleEntry]:
        """
        Mark entry as refined with LLM-processed text.

        Args:
            db: Database session
            entry_id: Entry ID
            user_id: User ID for authorization
            refined_text: Refined text from LLM

        Returns:
            Updated entry or None
        """
        entry = await self.get_entry(db, entry_id, user_id)
        if not entry:
            return None

        entry.refined_text = refined_text
        entry.is_refined = True
        await db.commit()
        await db.refresh(entry)
        return entry


# Global service instance
lifechronicle_db_service = LifeChronicleDBService()
