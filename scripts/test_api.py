import json

import requests

BASE_URL = "http://127.0.0.1:8000"


def test_endpoints():
    print("Testing API Endpoints...")
    print("=" * 50)

    # Test 1: Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/api/products/products/")
        print(f"1. Server status: {response.status_code}")
        if response.status_code == 200:
            print("   ✓ Server is running")
        else:
            print("   ✗ Server returned error")
    except Exception as e:
        print(f"   ✗ Cannot connect to server: {e}")
        return

    # Test 2: Get products (should work without auth)
    response = requests.get(f"{BASE_URL}/api/products/products/")
    print(f"\n2. Get products: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Found {len(data)} products")
    else:
        print(f"   ✗ Failed to get products: {response.text}")

    # Test 3: Get categories
    response = requests.get(f"{BASE_URL}/api/products/categories/")
    print(f"\n3. Get categories: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Found {len(data)} categories")
    else:
        print(f"   ✗ Failed to get categories: {response.text}")

    # Test 4: Try to register a user
    print("\n4. User registration test...")
    user_data = {
        "username": "testuser_api",
        "email": "testapi@example.com",
        "password": "TestPass123!",
        "password2": "TestPass123!",
        "first_name": "Test",
        "last_name": "API",
    }

    response = requests.post(f"{BASE_URL}/api/auth/register/", json=user_data)
    print(f"   Registration: {response.status_code}")
    if response.status_code == 201:
        print("   ✓ User registered successfully")
        user_info = response.json()
        print(f"   Username: {user_info.get('username')}")
    else:
        print(f"   ✗ Registration failed: {response.text}")

    # Test 5: Login
    print("\n5. User login test...")
    login_data = {"username": "testuser_api", "password": "TestPass123!"}

    response = requests.post(f"{BASE_URL}/api/auth/login/", json=login_data)
    print(f"   Login: {response.status_code}")

    if response.status_code == 200:
        login_info = response.json()
        token = login_info.get("token")
        print(f"   ✓ Login successful")
        print(f"   Token received: {token[:20]}...")

        # Use the token for authenticated requests
        headers = {"Authorization": f"Token {token}"}

        # Test 6: Get user profile
        response = requests.get(f"{BASE_URL}/api/auth/profile/", headers=headers)
        print(f"\n6. Get user profile: {response.status_code}")
        if response.status_code == 200:
            print("   ✓ Profile retrieved")

        # Test 7: Add item to cart
        print("\n7. Add item to cart test...")
        # First get a product ID
        products_response = requests.get(f"{BASE_URL}/api/products/products/")
        if products_response.status_code == 200:
            products = products_response.json().get("results", products_response.json())
            if products and len(products) > 0:
                product_id = products[0]["id"]
                cart_data = {"product_id": product_id, "quantity": 2}
                response = requests.post(
                    f"{BASE_URL}/api/cart/add_item/", headers=headers, json=cart_data
                )
                print(f"   Add to cart: {response.status_code}")
                if response.status_code == 200:
                    print("   ✓ Item added to cart")
                else:
                    print(f"   ✗ Failed to add to cart: {response.text}")

        # Test 8: Get cart
        response = requests.get(f"{BASE_URL}/api/cart/", headers=headers)
        print(f"\n8. Get cart: {response.status_code}")
        if response.status_code == 200:
            cart_data = response.json()
            print(f"   ✓ Cart retrieved")
            if isinstance(cart_data, list) and len(cart_data) > 0:
                cart = cart_data[0]
            else:
                cart = cart_data
            print(f"   Cart ID: {cart.get('id')}")
            print(f"   Items in cart: {len(cart.get('items', []))}")

    else:
        print(f"   ✗ Login failed: {response.text}")

    print("\n" + "=" * 50)
    print("API Testing Complete!")


if __name__ == "__main__":
    test_endpoints()
