#!/usr/bin/env python3
"""
Update Bar GPS coordinates via API
GPS: 41°21'40.7"N 2°06'59.0"E = 41.361305556, 2.116388889
"""
import requests
import json

API_URL = "https://general-backend-production-a734.up.railway.app"

print("📍 Updating GPS coordinates via API...")
print("   GPS: 41°21'40.7\"N 2°06'59.0\"E")
print("   Decimal: 41.361305556, 2.116388889\n")

# Step 1: Get admin token
print("🔑 Getting admin token...")
login_response = requests.post(
    f"{API_URL}/bar/admin/login",
    json={"username": "admin", "password": "senior"}
)

if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.status_code}")
    print(login_response.text)
    exit(1)

token = login_response.json()["access_token"]
print("✅ Token received\n")

# Step 2: Update GPS coordinates
print("🔄 Updating bar info with correct GPS...")
update_response = requests.put(
    f"{API_URL}/bar/admin/info",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "location_lat": "41.361305556",
        "location_lng": "2.116388889"
    }
)

print(f"Status: {update_response.status_code}")
if update_response.status_code == 200:
    print("✅ Update successful!")
    print(f"Response: {json.dumps(update_response.json(), indent=2)}\n")
else:
    print(f"❌ Update failed: {update_response.text}\n")
    exit(1)

# Step 3: Verify the update
print("🔍 Verifying GPS coordinates...")
verify_response = requests.get(f"{API_URL}/bar/info")
bar_info = verify_response.json()

lat = bar_info.get("location_lat")
lng = bar_info.get("location_lng")

print(f"Current GPS: lat={lat}, lng={lng}\n")

if lat == "41.361305556" and lng == "2.116388889":
    print("✅ GPS coordinates updated successfully!")
else:
    print(f"⚠️  GPS coordinates don't match expected values")
    print(f"   Expected: lat=41.361305556, lng=2.116388889")
    print(f"   Got: lat={lat}, lng={lng}")
