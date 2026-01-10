#!/usr/bin/env python3
"""
Clean up orphaned alembic_version entries that reference deleted migrations
Run this on Railway to fix migration issues
"""
import os
import sys
from sqlalchemy import create_engine, text

def cleanup_alembic():
    """Remove orphaned alembic version entries"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not set")
        return False

    # Fix URL for SQLAlchemy
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    try:
        engine = create_engine(database_url)

        with engine.connect() as conn:
            print("🔍 Current alembic versions:")
            result = conn.execute(text("SELECT version_num FROM alembic_version ORDER BY version_num;"))
            for row in result:
                print(f"   - {row[0]}")

            print("\n🧹 Cleaning up orphaned entries...")

            # Delete klassentreffen entries
            result = conn.execute(text("DELETE FROM alembic_version WHERE version_num LIKE '%klassentreffen%';"))
            deleted1 = result.rowcount

            # Delete 2026 entries (all Bar migrations were removed)
            result = conn.execute(text("DELETE FROM alembic_version WHERE version_num LIKE '2026%';"))
            deleted2 = result.rowcount

            # Delete cv_showcase if it's causing conflicts
            result = conn.execute(text("DELETE FROM alembic_version WHERE version_num = 'add_cv_showcase_001';"))
            deleted3 = result.rowcount

            conn.commit()

            total_deleted = deleted1 + deleted2 + deleted3
            print(f"   Deleted {total_deleted} orphaned entry/entries")

            print("\n📋 Remaining versions:")
            result = conn.execute(text("SELECT version_num FROM alembic_version ORDER BY version_num;"))
            for row in result:
                print(f"   - {row[0]}")

            print("\n✅ Cleanup complete! Backend should restart without migration errors.")
            return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = cleanup_alembic()
    sys.exit(0 if success else 1)
