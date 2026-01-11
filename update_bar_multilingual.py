#!/usr/bin/env python3
"""
Update script to convert cuisine, price_range, and rating to multilingual JSON objects
"""
import requests
import json

API_URL = "https://general-backend-production-a734.up.railway.app"

# Login to get admin token
login_response = requests.post(
    f"{API_URL}/bar/admin/login",
    json={"username": "admin", "password": "senior"}
)
token = login_response.json()["access_token"]

headers = {"Authorization": f"Bearer {token}"}

# Define multilingual data
multilingual_data = {
    "cuisine": {
        "ca": "Espanyola, Tapes, Mediterrània",
        "es": "Española, Tapas, Mediterránea",
        "en": "Spanish, Tapas, Mediterranean",
        "de": "Spanisch, Tapas, Mediterran",
        "fr": "Espagnole, Tapas, Méditerranéenne"
    },
    "price_range": {
        "ca": "€-€€",
        "es": "€-€€",
        "en": "€-€€",
        "de": "€-€€",
        "fr": "€-€€"
    },
    "rating": {
        "ca": "4.0/5 a Google",
        "es": "4.0/5 en Google",
        "en": "4.0/5 on Google",
        "de": "4.0/5 auf Google",
        "fr": "4.0/5 sur Google"
    }
}

# Update bar info
response = requests.put(
    f"{API_URL}/bar/admin/info",
    headers=headers,
    json=multilingual_data
)

if response.status_code == 200:
    print("✅ Successfully updated bar info with multilingual data")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
else:
    print(f"❌ Failed to update: {response.status_code}")
    print(response.text)
