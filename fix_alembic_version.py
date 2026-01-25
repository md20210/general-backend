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

            # Step 1: Check current versions
            result = conn.execute(text("SELECT version_num FROM alembic_version;"))
            old_versions = result.fetchall()

            if old_versions:
                print(f"⚠️  Found {len(old_versions)} existing version(s):", file=sys.stderr, flush=True)
                for v in old_versions:
                    print(f"   - {v[0]}", file=sys.stderr, flush=True)

                # Step 2: Check for specific problematic versions
                has_folder_attrs = any(v[0] == '20260119_folder_attrs' for v in old_versions)
                has_app_tracker = any(v[0] == '20260117_add_application_tracker' for v in old_versions)

                if has_folder_attrs or has_app_tracker:
                    print("🧹 Found problematic versions, clearing and resetting...", file=sys.stderr, flush=True)

                    # Delete all
                    conn.execute(text("DELETE FROM alembic_version;"))

                    # Insert correct base version
                    conn.execute(text("INSERT INTO alembic_version (version_num) VALUES ('20260117_add_app');"))
                    conn.commit()
                    print("✅ Database version reset to: 20260117_add_app", file=sys.stderr, flush=True)
                else:
                    print("✅ Versions look correct, no action needed", file=sys.stderr, flush=True)
            else:
                print("✅ Alembic version table is empty, migrations will start from scratch", file=sys.stderr, flush=True)

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
