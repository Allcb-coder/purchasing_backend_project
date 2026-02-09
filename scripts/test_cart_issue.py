import json

import requests

BASE_URL = "http://127.0.0.1:8000"

# 1. Register
print("1. Registering...")
response = requests.post(
    f"{BASE_URL}/api/auth/register/",
    json={
        "username": "carttest",
        "email": "cart@test.com",
        "password": "CartTest123!",
        "password2": "CartTest123!",
        "first_name": "Cart",
        "last_name": "Test",
    },
)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}\n")

# 2. Login
print("2. Logging in...")
response = requests.post(
    f"{BASE_URL}/api/auth/login/",
    json={"username": "carttest", "password": "CartTest123!"},
)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    token = response.json()["token"]
    headers = {"Authorization": f"Token {token}"}
    print(f"Token: {token[:30]}...\n")

    # 3. Get cart
    print("3. Getting cart...")
    response = requests.get(f"{BASE_URL}/api/cart/", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}\n")

    # 4. Try to get product
    print("4. Getting product...")
    response = requests.get(f"{BASE_URL}/api/products/products/")
    if response.status_code == 200:
        products = response.json().get("results", [])
        if products:
            product_id = products[0]["id"]
            print(f"Product ID: {product_id}\n")

            # 5. Add to cart
            print("5. Adding to cart...")
            response = requests.post(
                f"{BASE_URL}/api/cart/add_item/",
                headers=headers,
                json={"product_id": product_id, "quantity": 1},
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}\n")
