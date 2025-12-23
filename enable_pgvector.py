"""One-time script to enable pgvector extension."""
import asyncio
import asyncpg
from backend.config import settings

async def enable_pgvector():
    """Enable pgvector extension in PostgreSQL."""
    # Use asyncpg directly (not SQLAlchemy) for this admin task
    DATABASE_URL = settings.DATABASE_URL.replace("postgresql://", "").replace("postgresql+asyncpg://", "")

    print(f"Connecting to database...")

    try:
        # Connect directly with asyncpg
        conn = await asyncpg.connect(DATABASE_URL)

        # Enable pgvector extension
        print("Enabling pgvector extension...")
        await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        print("✅ pgvector extension enabled successfully!")

        # Verify it's installed
        result = await conn.fetch("SELECT * FROM pg_extension WHERE extname = 'vector';")
        if result:
            print(f"✅ Verified: pgvector extension is installed (version: {result[0]['extversion']})")
        else:
            print("⚠️ Warning: Could not verify pgvector installation")

        await conn.close()
        print("✅ Done!")

    except Exception as e:
        print(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(enable_pgvector())
