"""Temporary migration helper endpoint"""
from fastapi import APIRouter, Depends
from sqlalchemy import text
from backend.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/migration", tags=["migration"])

@router.post("/add-documents-column")
async def add_documents_column(
    db: AsyncSession = Depends(get_async_session)
):
    """Manually add documents column if it doesn't exist"""
    try:
        # Check if column exists
        check_query = text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name='job_applications'
            AND column_name='documents';
        """)
        result = await db.execute(check_query)
        exists = result.fetchone()

        if exists:
            return {"status": "Column already exists"}

        # Add column
        alter_query = text("""
            ALTER TABLE job_applications
            ADD COLUMN documents JSONB NOT NULL DEFAULT '{}';
        """)
        await db.execute(alter_query)
        await db.commit()

        return {"status": "Column added successfully"}
    except Exception as e:
        await db.rollback()
        return {"status": "error", "detail": str(e)}
