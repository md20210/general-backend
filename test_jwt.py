#!/usr/bin/env python3
"""Test JWT token generation"""
import asyncio
from backend.auth.jwt import get_jwt_strategy
from backend.models.user import User
from uuid import uuid4

async def test_jwt():
    # Create a mock user
    user = User(
        id=uuid4(),
        email="test@example.com",
        hashed_password="dummy",
        is_active=True,
        is_verified=True,
        is_superuser=True
    )

    # Generate token
    jwt_strategy = get_jwt_strategy()
    token = await jwt_strategy.write_token(user)

    print(f"✅ JWT Token generated successfully!")
    print(f"Token: {token[:50]}...")
    print(f"Length: {len(token)} characters")

if __name__ == "__main__":
    asyncio.run(test_jwt())
