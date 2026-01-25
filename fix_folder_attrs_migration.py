#!/usr/bin/env python3
"""
Fix the 20260119_folder_attrs migration issue on Railway database
"""
from sqlalchemy import create_engine, text

# Railway database connection
DATABASE_URL = "postgresql://postgres:QMsZIHABICYpgVtQSIxJgJHoGtptYlFZ@roundhouse.proxy.rlwy.net:35555/railway"

def fix_migration():
    """Check and fix the folder_attrs migration"""
    try:
        engine = create_engine(DATABASE_URL)

        with engine.connect() as conn:
            print("🔍 Step 1: Checking current alembic versions...")
            result = conn.execute(text("SELECT * FROM alembic_version;"))
            versions = result.fetchall()

            print(f"\n📋 Current version(s) in database:")
            for v in versions:
                print(f"   - version_num: {v[0]}")

            # Check if the problematic version exists
            result = conn.execute(text("SELECT version_num FROM alembic_version WHERE version_num = '20260119_folder_attrs';"))
            problematic_version = result.fetchone()

            if problematic_version:
                print(f"\n⚠️  Found problematic version: {problematic_version[0]}")
                print("🧹 Step 2: Deleting the problematic version...")

                result = conn.execute(text("DELETE FROM alembic_version WHERE version_num = '20260119_folder_attrs';"))
                deleted = result.rowcount
                conn.commit()

                print(f"✅ Deleted {deleted} row(s)")
            else:
                print(f"\n✅ Version '20260119_folder_attrs' not found in database")
                print("   Looking for similar versions...")

                # Check for similar versions
                result = conn.execute(text("SELECT version_num FROM alembic_version WHERE version_num LIKE '20260119%';"))
                similar_versions = result.fetchall()

                if similar_versions:
                    print(f"\n📋 Found similar versions:")
                    for v in similar_versions:
                        print(f"   - {v[0]}")
                else:
                    print("   No similar versions found")

            print("\n📋 Final state - Remaining versions:")
            result = conn.execute(text("SELECT version_num FROM alembic_version ORDER BY version_num;"))
            remaining = result.fetchall()
            for v in remaining:
                print(f"   - {v[0]}")

            print("\n✅ Migration fix completed!")
            return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    fix_migration()
