#!/usr/bin/env python3
"""
Test newsletter endpoint and diagnose issues
"""
import requests
import json

API_URL = "https://general-backend-production-a734.up.railway.app"

print("🔍 Newsletter Diagnostic Test\n")

# Test 1: Check if bar/info works
print("1️⃣ Testing bar/info endpoint...")
try:
    response = requests.get(f"{API_URL}/bar/info", timeout=10)
    if response.status_code == 200:
        print("   ✅ bar/info works")
        data = response.json()
        print(f"   GPS: {data.get('location_lat')}, {data.get('location_lng')}")
    else:
        print(f"   ❌ bar/info failed: {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print()

# Test 2: Try newsletter subscription
print("2️⃣ Testing newsletter subscription...")
try:
    response = requests.post(
        f"{API_URL}/bar/newsletter",
        json={"email": "diagnostic@test.com", "name": "Diagnostic", "language": "en"},
        timeout=10
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text[:200]}")

    if response.status_code == 201:
        print("   ✅ Newsletter subscription works!")
        print(f"   Data: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"   ❌ Newsletter failed: {response.status_code}")

except Exception as e:
    print(f"   ❌ Error: {e}")

print()

# Test 3: Try to get admin subscribers (will fail if table doesn't exist)
print("3️⃣ Testing admin login...")
try:
    login_response = requests.post(
        f"{API_URL}/bar/admin/login",
        json={"username": "admin", "password": "senior"},
        timeout=10
    )

    if login_response.status_code == 200:
        token = login_response.json()["access_token"]
        print("   ✅ Admin login works")

        print("\n4️⃣ Testing get subscribers...")
        subscribers_response = requests.get(
            f"{API_URL}/bar/admin/newsletter/subscribers",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )

        print(f"   Status: {subscribers_response.status_code}")
        if subscribers_response.status_code == 200:
            print("   ✅ Get subscribers works!")
            print(f"   Subscribers: {subscribers_response.json()}")
        else:
            print(f"   ❌ Get subscribers failed: {subscribers_response.text[:200]}")
    else:
        print(f"   ❌ Admin login failed: {login_response.status_code}")

except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n✅ Diagnostic complete")
