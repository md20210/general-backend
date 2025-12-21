"""Test user registration to debug bcrypt error."""
import asyncio
import sys
from backend.database import get_async_session, create_db_and_tables
from backend.auth.users import get_user_manager, get_user_db
from backend.schemas.user import UserCreate


async def test_registration():
    """Test user registration."""
    print("Creating database tables...")
    await create_db_and_tables()

    print("Testing user registration...")

    # Create test user data
    user_data = UserCreate(
        email="admin@dabrock.info",
        password="Test1234!",
        is_active=True,
        is_superuser=False,
        is_verified=False,
        is_admin=False
    )

    print(f"User data: {user_data}")
    print(f"Password length: {len(user_data.password)} chars")
    print(f"Password bytes: {len(user_data.password.encode('utf-8'))} bytes")

    # Get database session
    async for session in get_async_session():
        # Get user database
        async for user_db in get_user_db(session):
            # Get user manager
            async for user_manager in get_user_manager(user_db):
                try:
                    # Try to create user
                    print("Calling user_manager.create()...")
                    user = await user_manager.create(user_data)
                    print(f"✅ User created successfully: {user.email}")
                    return True
                except Exception as e:
                    print(f"❌ Error creating user: {e}")
                    import traceback
                    traceback.print_exc()
                    return False


if __name__ == "__main__":
    result = asyncio.run(test_registration())
    sys.exit(0 if result else 1)
