"""
Quick end-to-end test script for the auth + children flow.
Run with: python test_auth.py
"""

import requests
 
BASE_URL = "http://localhost:8000/api"
 
EMAIL = "test@test.com"
PASSWORD = "string"
 
# 1. Login
login_resp = requests.post(
    f"{BASE_URL}/auth/login",
    json={"email": EMAIL, "password": PASSWORD},
)
print("LOGIN STATUS:", login_resp.status_code)
print("LOGIN BODY:", login_resp.json())
 
if login_resp.status_code != 200:
    raise SystemExit("Login failed - stopping here.")
 
token = login_resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
 
# 2. Create a child
create_resp = requests.post(
    f"{BASE_URL}/children",
    json={
        "first_name": "Test",
        "date_of_birth": "2023-01-01",
        "allergies": "peanuts, tree nuts",
        "medical_notes": "mild eczema, seen by pediatrician quarterly",
    },
    headers=headers,
)
print("\nCREATE CHILD STATUS:", create_resp.status_code)
print("CREATE CHILD BODY:", create_resp.json())
 
# 3. List children
list_resp = requests.get(f"{BASE_URL}/children", headers=headers)
print("\nLIST CHILDREN STATUS:", list_resp.status_code)
print("LIST CHILDREN BODY:", list_resp.json())
