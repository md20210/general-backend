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

# Now import and run uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8080,
    )
