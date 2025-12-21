"""Database configuration and session management."""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
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


async def create_db_and_tables():
    """Create all database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
