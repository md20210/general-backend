#!/usr/bin/env python3
"""Direct database script to make a user admin"""
import os
import sys
from sqlalchemy import create_engine, text

# Database connection
DATABASE_URL = "postgresql://postgres:QMsZIHABICYpgVtQSIxJgJHoGtptYlFZ@autorack.proxy.rlwy.net:33155/railway"

def make_admin(email: str):
    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
        # Check if user exists
        result = conn.execute(
            text("SELECT id, email, is_superuser FROM users WHERE email = :email"),
            {"email": email}
        )
        user = result.fetchone()

        if not user:
            print(f"❌ User {email} not found!")
            return False

        print(f"📧 Found user: {user[1]}")
        print(f"   Current admin status: {user[2]}")

        # Make admin
        conn.execute(
            text("""
                UPDATE users
                SET is_superuser = true, is_active = true, is_verified = true
                WHERE email = :email
            """),
            {"email": email}
        )
        conn.commit()

        print(f"✅ User {email} is now an admin!")
        return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 make_admin.py <email>")
        sys.exit(1)

    email = sys.argv[1]
    make_admin(email)
