import requests
import json

BASE_URL = "http://127.0.0.1:8000"

print("Debugging API endpoints...\n")

# Test 1: Check products endpoint
print("1. Testing /api/products/products/")
response = requests.get(f"{BASE_URL}/api/products/products/")
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"   Count: {data.get('count', 'N/A')}")
    print(f"   Has results: {'results' in data}")
    if 'results' in data and len(data['results']) > 0:
        print(f"   First product: {data['results'][0]['name']}")
        print(f"   First product ID: {data['results'][0]['id']}")
else:
    print(f"   Error: {response.text}")

# Test 2: Try to register a user
print("\n2. Testing user registration")
user_data = {
    "username": f"debug_user_{hash('test')}",
    "email": "debug@example.com",
    "password": "DebugPass123!",
    "password2": "DebugPass123!",
    "first_name": "Debug",
    "last_name": "User"
}
response = requests.post(f"{BASE_URL}/api/auth/register/", json=user_data)
print(f"   Status: {response.status_code}")
if response.status_code in [200, 201]:
    print("   ✓ Registration successful")
    user_data = response.json()
    print(f"   Username: {user_data.get('username')}")
else:
    print(f"   Error: {response.text}")

# Test 3: Try to login
print("\n3. Testing login")
login_data = {
    "username": user_data["username"],
    "password": "DebugPass123!"
}
response = requests.post(f"{BASE_URL}/api/auth/login/", json=login_data)
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    print("   ✓ Login successful")
    token_data = response.json()
    token = token_data.get('token')
    print(f"   Token: {token[:30]}...")
    
    # Test 4: Add to cart with token
    print("\n4. Testing add to cart")
    headers = {"Authorization": f"Token {token}"}
    
    # First get a product ID
    prod_response = requests.get(f"{BASE_URL}/api/products/products/")
    if prod_response.status_code == 200:
        products = prod_response.json().get('results', [])
        if products:
            product_id = products[0]['id']
            print(f"   Using product ID: {product_id}")
            
            cart_data = {"product_id": product_id, "quantity": 1}
            cart_response = requests.post(
                f"{BASE_URL}/api/cart/add_item/",
                headers=headers,
                json=cart_data
            )
            print(f"   Add to cart status: {cart_response.status_code}")
            print(f"   Response: {cart_response.text[:100]}")
else:
    print(f"   Error: {response.text}")

print("\nDebug complete!")
