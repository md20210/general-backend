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

# Run Alembic migrations before starting server
if __name__ == "__main__":
    import subprocess
    import os

    # Only run migrations if DATABASE_URL is set (production)
    if os.getenv("DATABASE_URL"):
        print("🔄 Running database migrations...", file=sys.stderr, flush=True)
        try:
            result = subprocess.run(
                ["python3", "-c", "from alembic.config import Config; from alembic import command; cfg = Config('alembic.ini'); command.upgrade(cfg, 'head')"],
                capture_output=True,
                text=True,
                check=True
            )
            print("✅ Database migrations completed", file=sys.stderr, flush=True)
            if result.stdout:
                print(result.stdout, file=sys.stderr, flush=True)
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Migration failed: {e.stderr}", file=sys.stderr, flush=True)
            print("⚠️  Continuing anyway (migrations might already be applied)", file=sys.stderr, flush=True)

    # Now import and run uvicorn
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8080,
    )
