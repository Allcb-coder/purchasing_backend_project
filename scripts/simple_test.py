import json
import time

import requests

BASE_URL = "http://127.0.0.1:8000"


def run_test():
    print("Starting simple test...\n")

    # 1. Register
    username = f"testuser_{int(time.time())}"
    print(f"1. Registering {username}...")
    response = requests.post(
        f"{BASE_URL}/api/auth/register/",
        json={
            "username": username,
            "email": f"{username}@example.com",
            "password": "TestPass123!",
            "password2": "TestPass123!",
            "first_name": "Test",
            "last_name": "User",
        },
    )
    print(f"   Status: {response.status_code}")

    # 2. Login
    print(f"\n2. Logging in {username}...")
    response = requests.post(
        f"{BASE_URL}/api/auth/login/",
        json={"username": username, "password": "TestPass123!"},
    )

    if response.status_code != 200:
        print(f"   Login failed: {response.text}")
        return

    token = response.json()["token"]
    headers = {"Authorization": f"Token {token}"}
    print(f"   Login successful")

    # 3. Get products
    print("\n3. Getting products...")
    response = requests.get(f"{BASE_URL}/api/products/products/")
    if response.status_code == 200:
        products = response.json().get("results", [])
        if products:
            product_id = products[0]["id"]
            product_name = products[0]["name"]
            print(f"   Found product: {product_name} (ID: {product_id})")

            # 4. Add to cart
            print(f"\n4. Adding to cart...")
            response = requests.post(
                f"{BASE_URL}/api/cart/",
                headers=headers,
                json={"product_id": product_id, "quantity": 1},
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   Added to cart successfully")

                # 5. View cart
                print(f"\n5. Viewing cart...")
                response = requests.get(f"{BASE_URL}/api/cart/", headers=headers)
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    cart = response.json()
                    print(f"   Cart ID: {cart.get('id')}")
                    print(f"   Items: {cart.get('total_items', 0)}")
                    print(f"   Total: ${cart.get('total', 0)}")

                    # 6. Create order
                    print(f"\n6. Creating order...")
                    response = requests.post(
                        f"{BASE_URL}/api/orders/",
                        headers=headers,
                        json={
                            "first_name": "Test",
                            "last_name": "User",
                            "email": f"{username}@example.com",
                            "phone": "+1234567890",
                            "address": "123 Test St",
                            "city": "Test City",
                            "postal_code": "12345",
                            "country": "Testland",
                            "notes": "Test order",
                        },
                    )
                    print(f"   Status: {response.status_code}")
                    if response.status_code == 201:
                        order = response.json()
                        print(f"   Order created! ID: {order.get('id')}")
                        print(f"   Order total: ${order.get('total')}")
                        print(f"   Order status: {order.get('status_display')}")

                        # 7. View orders
                        print(f"\n7. Viewing orders...")
                        response = requests.get(
                            f"{BASE_URL}/api/orders/", headers=headers
                        )
                        print(f"   Status: {response.status_code}")
                        if response.status_code == 200:
                            orders = response.json()
                            print(f"   Found {len(orders)} orders")
                    else:
                        print(f"   Order failed: {response.text}")
                else:
                    print(f"   View cart failed: {response.text}")
            else:
                print(f"   Add to cart failed: {response.text}")
        else:
            print("   No products found")
    else:
        print(f"   Get products failed: {response.status_code}")

    print("\nTest complete!")


if __name__ == "__main__":
    run_test()
