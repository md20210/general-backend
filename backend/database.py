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


# Synchronous session for compatibility with older endpoints
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

# Create synchronous engine
sync_engine = create_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql://"),
    echo=True if settings.LOG_LEVEL == "DEBUG" else False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Synchronous session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)


def get_db() -> Generator[Session, None, None]:
    """Dependency to get synchronous database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


import asyncio
import logging

logger = logging.getLogger(__name__)

# Import all models to register them with Base.metadata
from backend.models.user import User  # noqa: F401
from backend.models.project import Project  # noqa: F401
from backend.models.jobassistant import JobApplication  # noqa: F401
from backend.models.elasticsearch_showcase import UserElasticProfile, ElasticJobAnalysis, ComparisonResult  # noqa: F401
from backend.models.bar import BarInfo, BarNewsletter  # noqa: F401

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

                # Add missing LLM analysis columns if they don't exist
                await conn.execute(text("""
                    DO $$
                    BEGIN
                        -- Add job_analysis column if it doesn't exist
                        IF NOT EXISTS (
                            SELECT 1 FROM information_schema.columns
                            WHERE table_name = 'elastic_job_analyses'
                            AND column_name = 'job_analysis'
                        ) THEN
                            ALTER TABLE elastic_job_analyses
                            ADD COLUMN job_analysis JSONB NOT NULL DEFAULT '{}';
                        END IF;

                        -- Add fit_score column if it doesn't exist
                        IF NOT EXISTS (
                            SELECT 1 FROM information_schema.columns
                            WHERE table_name = 'elastic_job_analyses'
                            AND column_name = 'fit_score'
                        ) THEN
                            ALTER TABLE elastic_job_analyses
                            ADD COLUMN fit_score JSONB NOT NULL DEFAULT '{}';
                        END IF;

                        -- Add success_probability column if it doesn't exist
                        IF NOT EXISTS (
                            SELECT 1 FROM information_schema.columns
                            WHERE table_name = 'elastic_job_analyses'
                            AND column_name = 'success_probability'
                        ) THEN
                            ALTER TABLE elastic_job_analyses
                            ADD COLUMN success_probability JSONB NOT NULL DEFAULT '{}';
                        END IF;
                    END $$;
                """))

            logger.info("✅ Database tables created/verified and pgvector enabled")
            return  # Erfolg → raus aus der Funktion

        except Exception as e:
            logger.warning(f"DB connection attempt {attempt}/{max_attempts} failed: {e}")
            if attempt == max_attempts:
                logger.error("Could not connect to database after multiple attempts")
                raise  # Let the app crash if all attempts fail
            await asyncio.sleep(delay)
