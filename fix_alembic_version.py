#!/usr/bin/env python3
"""
Fix alembic_version table before running migrations.
This script removes the incorrect version entry '20260119_folder_attrs'.
"""
import os
import sys


def fix_alembic_version():
    """Remove incorrect alembic version entry"""
    try:
        from sqlalchemy import create_engine, text

        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            print("⚠️  DATABASE_URL not set, skipping alembic fix", file=sys.stderr, flush=True)
            return True

        # Fix URL for SQLAlchemy
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)

        engine = create_engine(database_url)

        with engine.connect() as conn:
            print("🔍 Checking alembic_version table...", file=sys.stderr, flush=True)

            # Check if the problematic version exists
            result = conn.execute(text("SELECT version_num FROM alembic_version WHERE version_num = '20260119_folder_attrs';"))
            problematic_version = result.fetchone()

            if problematic_version:
                print(f"⚠️  Found incorrect version: {problematic_version[0]}", file=sys.stderr, flush=True)
                print("🧹 Removing incorrect version entry...", file=sys.stderr, flush=True)

                conn.execute(text("DELETE FROM alembic_version WHERE version_num = '20260119_folder_attrs';"))
                conn.commit()

                print("✅ Incorrect version removed successfully!", file=sys.stderr, flush=True)
            else:
                print("✅ No problematic version found, database is clean", file=sys.stderr, flush=True)

            # Show current versions
            result = conn.execute(text("SELECT version_num FROM alembic_version ORDER BY version_num;"))
            versions = result.fetchall()

            if versions:
                print(f"📋 Current alembic versions ({len(versions)}):", file=sys.stderr, flush=True)
                for v in versions:
                    print(f"   - {v[0]}", file=sys.stderr, flush=True)
            else:
                print("📋 No alembic versions in database yet", file=sys.stderr, flush=True)

        return True

    except ImportError:
        print("⚠️  SQLAlchemy not installed, skipping alembic fix", file=sys.stderr, flush=True)
        return True
    except Exception as e:
        print(f"❌ Error fixing alembic version: {e}", file=sys.stderr, flush=True)
        # Don't fail the deployment, just warn
        return True


if __name__ == "__main__":
    fix_alembic_version()
