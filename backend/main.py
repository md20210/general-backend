"""Main FastAPI application."""
# MUST be first - monkey-patch passlib before any imports use it
import backend.patch_passlib  # noqa: F401

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
import os
from pathlib import Path
from backend.config import settings
from backend.database import create_db_and_tables
from backend.api.auth import auth_router, users_router
from backend.api.admin import router as admin_router
from backend.api.llm import router as llm_router
from backend.api.projects import router as projects_router
from backend.api.documents import router as documents_router
from backend.api.chat import router as chat_router
from backend.api.reports import router as reports_router
from backend.api.translations import router as translations_router
from backend.api.crawler import router as crawler_router
from backend.api.privategxt import router as privategxt_router
from backend.api.lifechronicle import router as lifechronicle_router
from backend.api.speech import router as speech_router
from backend.api.demo_auth import router as demo_auth_router
from backend.api.jobassistant import router as jobassistant_router
from backend.api.migration_helper import router as migration_router
from backend.api.elasticsearch_showcase import router as elasticsearch_router

# Setup logging
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info("Starting General Backend...")
    await create_db_and_tables()
    logger.info("Database tables created/verified")

    # Run Alembic migrations automatically in a thread pool to avoid event loop conflicts
    try:
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        from alembic.config import Config
        from alembic import command

        logger.info("Running Alembic migrations...")
        alembic_cfg = Config("alembic.ini")

        # Run migrations in a thread pool executor to avoid event loop conflicts
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            await loop.run_in_executor(executor, command.upgrade, alembic_cfg, "head")

        logger.info("✅ Alembic migrations completed successfully")
    except Exception as e:
        logger.warning(f"⚠️  Alembic migrations failed (non-critical): {e}")

    yield
    # Shutdown
    logger.info("Shutting down General Backend...")


# Create FastAPI app
# CV_SHOWCASE enum now added - restarting to refresh all DB connection pools
app = FastAPI(
    title="General Backend",
    description="Central backend for all showcases (CV Matcher, PrivateGxT, LifeChronicle)",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Middleware
# Always include production frontend origin
cors_origins = list(set(settings.allowed_origins_list + [
    "https://www.dabrock.info",
    "https://dabrock.info",
    "http://dabrock.info",
    "http://www.dabrock.info",
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:3000",
    "http://localhost:3001"
]))
logger.info(f"CORS allowed origins: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(admin_router)
app.include_router(llm_router)
app.include_router(projects_router)
app.include_router(documents_router)
app.include_router(chat_router)
app.include_router(reports_router)
app.include_router(translations_router)
app.include_router(crawler_router)
app.include_router(privategxt_router)
app.include_router(lifechronicle_router)
app.include_router(speech_router)
app.include_router(demo_auth_router)
app.include_router(jobassistant_router)
app.include_router(migration_router)
app.include_router(elasticsearch_router)

# Mount static files for uploads (LifeChronicle photos, etc.)
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "./uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")
logger.info(f"Static files mounted: /uploads -> {UPLOAD_DIR}")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "General Backend API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "database": "connected",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=True,
    )
