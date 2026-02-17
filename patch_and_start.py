#!/usr/bin/env python3
"""Patch bcrypt before starting uvicorn."""
import sys

# PATCH BCRYPT FIRST - before ANY other imports
import bcrypt

_original_hashpw = bcrypt.hashpw
_original_checkpw = bcrypt.checkpw


def patched_hashpw(password, salt):
    """Truncate password to 72 bytes."""
    if isinstance(password, str):
        password = password.encode('utf-8')
    if len(password) > 72:
        password = password[:72]
    return _original_hashpw(password, salt)


def patched_checkpw(password, hashed):
    """Truncate password to 72 bytes."""
    if isinstance(password, str):
        password = password.encode('utf-8')
    if len(password) > 72:
        password = password[:72]
    return _original_checkpw(password, hashed)


bcrypt.hashpw = patched_hashpw
bcrypt.checkpw = patched_checkpw

print("✅ Bcrypt patched - passwords truncated to 72 bytes", file=sys.stderr, flush=True)


def wait_for_db(database_url: str, max_attempts: int = 30, delay: int = 3) -> bool:
    """Wait until PostgreSQL is ready to accept connections."""
    import time
    import psycopg2

    # Convert asyncpg URL to psycopg2 URL if needed
    db_url = database_url.replace("postgresql+asyncpg://", "postgresql://")

    print(f"⏳ Waiting for database to be ready...", file=sys.stderr, flush=True)
    for attempt in range(1, max_attempts + 1):
        try:
            conn = psycopg2.connect(db_url, connect_timeout=5)
            conn.close()
            print(f"✅ Database is ready (attempt {attempt})", file=sys.stderr, flush=True)
            return True
        except psycopg2.OperationalError as e:
            print(f"⏳ DB not ready yet (attempt {attempt}/{max_attempts}): {e}", file=sys.stderr, flush=True)
            if attempt < max_attempts:
                time.sleep(delay)

    print("❌ Database did not become ready in time", file=sys.stderr, flush=True)
    return False


def run_alembic_migrations(max_attempts: int = 5, delay: int = 5) -> bool:
    """Run Alembic migrations with retry logic."""
    import time
    import subprocess

    print("🔄 Running database migrations...", file=sys.stderr, flush=True)
    for attempt in range(1, max_attempts + 1):
        try:
            result = subprocess.run(
                [
                    "python3", "-c",
                    "from alembic.config import Config; from alembic import command; "
                    "cfg = Config('alembic.ini'); command.upgrade(cfg, 'head')"
                ],
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode == 0:
                print("✅ Database migrations completed", file=sys.stderr, flush=True)
                if result.stdout:
                    print(result.stdout, file=sys.stderr, flush=True)
                return True
            else:
                print(
                    f"⚠️  Migration attempt {attempt}/{max_attempts} failed (exit {result.returncode}): "
                    f"{result.stderr[-500:] if result.stderr else 'no output'}",
                    file=sys.stderr, flush=True
                )
        except subprocess.TimeoutExpired:
            print(f"⚠️  Migration attempt {attempt}/{max_attempts} timed out", file=sys.stderr, flush=True)
        except Exception as e:
            print(f"⚠️  Migration attempt {attempt}/{max_attempts} error: {e}", file=sys.stderr, flush=True)

        if attempt < max_attempts:
            print(f"⏳ Retrying migrations in {delay}s...", file=sys.stderr, flush=True)
            time.sleep(delay)

    print("⚠️  All migration attempts failed - continuing anyway (may already be applied)", file=sys.stderr, flush=True)
    return False


# Run Alembic migrations before starting server
if __name__ == "__main__":
    import os

    database_url = os.getenv("DATABASE_URL", "")

    if database_url:
        # Step 1: Wait for DB to be ready before doing anything
        db_ready = wait_for_db(database_url)

        if not db_ready:
            print("❌ Cannot start: database is not available", file=sys.stderr, flush=True)
            sys.exit(1)

        # Step 2: Run migrations (with retry)
        run_alembic_migrations()
    else:
        print("⚠️  No DATABASE_URL set - skipping DB wait and migrations", file=sys.stderr, flush=True)

    # Step 3: Start uvicorn
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    print(f"🚀 Starting server on port {port}...", file=sys.stderr, flush=True)
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=port,
    )
