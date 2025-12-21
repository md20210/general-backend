"""Database configuration and session management."""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text
from typing import AsyncGenerator
from backend.config import settings


# Convert postgres:// to postgresql+asyncpg://
DATABASE_URL = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# SQLAlchemy async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True if settings.LOG_LEVEL == "DEBUG" else False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get async database session."""
    async with async_session_maker() as session:
        yield session

import asyncio
import logging

logger = logging.getLogger(__name__)

async def create_db_and_tables():
    """Create all database tables and enable pgvector extension with retry logic."""
    max_attempts = 30
    delay = 2  # seconds

    for attempt in range(1, max_attempts + 1):
        try:
            async with engine.begin() as conn:
                # Enable pgvector extension
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                # Create tables
                await conn.run_sync(Base.metadata.create_all)
            logger.info("✅ Database tables created/verified and pgvector enabled")
            return  # Erfolg → raus aus der Funktion

        except Exception as e:
            logger.warning(f"DB connection attempt {attempt}/{max_attempts} failed: {e}")
            if attempt == max_attempts:
                logger.error("Could not connect to database after multiple attempts")
                raise  # Let the app crash if all attempts fail
            await asyncio.sleep(delay)
