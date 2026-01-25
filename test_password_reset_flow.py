#!/usr/bin/env python3
"""Test password reset flow to identify the issue."""
import requests
import time

API_URL = "https://general-backend-production-a734.up.railway.app"

print("🧪 Testing Password Reset Flow")
print("=" * 60)

# Step 1: Request password reset
print("\n1️⃣ Requesting password reset...")
response = requests.post(
    f"{API_URL}/api/mvp-auth/password-reset-request",
    json={"email": "michael.dabrock@gmx.es"}
)
print(f"   Status: {response.status_code}")
print(f"   Response: {response.json()}")

print("\n⏳ Waiting 5 seconds for email to be sent...")
time.sleep(5)

print("\n📧 Check your email for the reset link!")
print("   Email from: onboarding@resend.dev")
print("   Copy the token from the URL (after ?token=)")
print("\n2️⃣ When you have the token, we'll test the confirm endpoint")

# Get token from user
token = input("\nPaste the token here: ").strip()

# Step 2: Attempt to reset password
print(f"\n3️⃣ Attempting to reset password with token: {token[:20]}...")
response = requests.post(
    f"{API_URL}/api/mvp-auth/password-reset-confirm",
    json={
        "token": token,
        "new_password": "NewTestPassword123!"
    }
)

print(f"   Status: {response.status_code}")
print(f"   Response: {response.text}")

if response.status_code == 200:
    print("\n✅ SUCCESS! Password reset worked!")
else:
    print(f"\n❌ FAILED with status {response.status_code}")
    print("   This helps identify the issue.")
