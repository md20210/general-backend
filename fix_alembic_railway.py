#!/usr/bin/env python3
"""
Fix Alembic multiple heads error on Railway database
"""
import psycopg2
import os

# Railway database connection
DB_HOST = "roundhouse.proxy.rlwy.net"
DB_PORT = 35555
DB_NAME = "railway"
DB_USER = "postgres"
DB_PASSWORD = "QMsZIHABICYpgVtQSIxJgJHoGtptYlFZ"

def fix_alembic():
    """Clean up problematic alembic version entries"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cur = conn.cursor()

        print("🔍 Checking current alembic versions...")
        cur.execute("SELECT version_num FROM alembic_version ORDER BY version_num;")
        versions = cur.fetchall()

        print(f"\n📋 Current versions in database:")
        for v in versions:
            print(f"   - {v[0]}")

        print("\n🧹 Cleaning up problematic versions...")

        # Delete all 2026 versions
        cur.execute("DELETE FROM alembic_version WHERE version_num LIKE '2026%';")
        deleted = cur.getrowcount()
        print(f"   Deleted {deleted} version(s) starting with '2026'")

        # Delete cv_showcase head that causes conflict
        cur.execute("DELETE FROM alembic_version WHERE version_num = 'add_cv_showcase_001';")
        deleted2 = cur.getrowcount()
        if deleted2 > 0:
            print(f"   Deleted cv_showcase version")

        conn.commit()

        print("\n✅ Alembic cleanup completed!")

        # Show remaining versions
        cur.execute("SELECT version_num FROM alembic_version ORDER BY version_num;")
        remaining = cur.fetchall()
        print(f"\n📋 Remaining versions:")
        for v in remaining:
            print(f"   - {v[0]}")

        cur.close()
        conn.close()

        print("\n🎉 Backend should now be able to start without 'multiple heads' error!")

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

    return True

if __name__ == "__main__":
    fix_alembic()
