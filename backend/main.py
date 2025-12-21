"""Main FastAPI application."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from backend.config import settings
from backend.database import create_db_and_tables
from backend.api.auth import auth_router, users_router
from backend.api.admin import router as admin_router
from backend.api.llm import router as llm_router
from backend.api.projects import router as projects_router
from backend.api.documents import router as documents_router

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
    yield
    # Shutdown
    logger.info("Shutting down General Backend...")


# Create FastAPI app
app = FastAPI(
    title="General Backend",
    description="Central backend for all showcases (CV Matcher, PrivateGPT, TellMeLife)",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
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
