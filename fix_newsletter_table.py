#!/usr/bin/env python3
"""
Fix bar_newsletter table - add missing language column
"""
import requests

API_URL = "https://general-backend-production-a734.up.railway.app"

print("🔧 Fixing bar_newsletter table...\n")

# Get admin token
print("🔑 Getting admin token...")
login_response = requests.post(
    f"{API_URL}/bar/admin/login",
    json={"username": "admin", "password": "senior"}
)

if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.status_code}")
    exit(1)

token = login_response.json()["access_token"]
print("✅ Token received\n")

# The fix needs to be done via SQL, but we can't execute arbitrary SQL via API
# Let's create a migration file instead

print("⚠️  The bar_newsletter table exists but is missing the 'language' column")
print("    This needs to be fixed with SQL:")
print()
print("    ALTER TABLE bar_newsletter ADD COLUMN IF NOT EXISTS language VARCHAR(5) DEFAULT 'ca';")
print()
print("    This should be run on the Railway database directly.")
print()
print("Alternatively, drop and recreate the table:")
print("    DROP TABLE IF EXISTS bar_newsletter;")
print("    -- Then the CREATE TABLE statement from database.py will run on next restart")
