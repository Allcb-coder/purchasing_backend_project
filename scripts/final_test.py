import json
import time

import requests

BASE_URL = "http://127.0.0.1:8000"


class TestRunner:
    def __init__(self):
        self.token = None
        self.headers = None
        self.username = None

    def print_step(self, num, desc):
        print(f"\n{'=' * 60}")
        print(f"STEP {num}: {desc}")
        print("=" * 60)

    def step1_register(self):
        self.print_step(1, "REGISTER USER")
        self.username = f"finaltest_{int(time.time())}"

        response = requests.post(
            f"{BASE_URL}/api/auth/register/",
            json={
                "username": self.username,
                "email": f"{self.username}@example.com",
                "password": "FinalTest123!",
                "password2": "FinalTest123!",
                "first_name": "Final",
                "last_name": "Test",
            },
        )

        if response.status_code in [200, 201]:
            print("✓ User registered")
            return True
        else:
            print(f"✗ Registration failed: {response.text}")
            return False

    def step2_login(self):
        self.print_step(2, "LOGIN")
        response = requests.post(
            f"{BASE_URL}/api/auth/login/",
            json={"username": self.username, "password": "FinalTest123!"},
        )

        if response.status_code == 200:
            self.token = response.json()["token"]
            self.headers = {"Authorization": f"Token {self.token}"}
            print("✓ Login successful")
            return True
        else:
            print(f"✗ Login failed: {response.text}")
            return False

    def step3_get_products(self):
        self.print_step(3, "GET PRODUCTS")
        response = requests.get(f"{BASE_URL}/api/products/products/")

        if response.status_code == 200:
            data = response.json()
            products = data.get("results", [])
            print(f"✓ Found {len(products)} products")

            if products:
                self.product_id = products[0]["id"]
                self.product_name = products[0]["name"]
                print(f"  Selected: {self.product_name} (ID: {self.product_id})")
                return True
        else:
            print(f"✗ Failed: {response.status_code}")
        return False

    def step4_add_to_cart(self):
        self.print_step(4, "ADD TO CART")

    response = requests.post(
        f"{BASE_URL}/api/cart/",  # This is correct
        headers=self.headers,
        json={"product_id": self.product_id, "quantity": 2},
    )

    if response.status_code == 200:
        print("✓ Added to cart")
        return True
    else:
        print(f"✗ Failed: {response.text[:100]}")  # Show only first 100 chars
        return False


def step5_view_cart(self):
    self.print_step(5, "VIEW CART")
    response = requests.get(f"{BASE_URL}/api/cart/", headers=self.headers)

    if response.status_code == 200:
        cart = response.json()
        print("✓ Cart retrieved")
        print(f"  Items: {cart.get('total_items', 0)}")
        print(f"  Total: ${cart.get('total', 0)}")
        return True
    else:
        print(f"✗ Failed: {response.text}")
        return False


def step6_create_order(self):
    self.print_step(6, "CREATE ORDER")
    response = requests.post(
        f"{BASE_URL}/api/orders/",
        headers=self.headers,
        json={
            "first_name": "Final",
            "last_name": "Test",
            "email": f"{self.username}@example.com",
            "phone": "+1234567890",
            "address": "123 Final St",
            "city": "Final City",
            "postal_code": "54321",
            "country": "Finland",
            "notes": "Final test order",
        },
    )

    if response.status_code == 201:
        order = response.json()
        print("✓ Order created!")
        print(f"  Order ID: {order.get('id')}")
        print(f"  Status: {order.get('status_display')}")
        print(f"  Total: ${order.get('total')}")
        return True
    else:
        print(f"✗ Failed: {response.text}")
        return False


def step7_view_orders(self):
    self.print_step(7, "VIEW ORDERS")
    response = requests.get(f"{BASE_URL}/api/orders/", headers=self.headers)

    if response.status_code == 200:
        orders = response.json()
        print(f"✓ Found {len(orders)} orders")
        for order in orders:
            print(
                f"  Order #{order.get('id')}: ${order.get('total')} - {order.get('status_display')}"
            )
        return True
    else:
        print(f"✗ Failed: {response.text}")
        return False


def run(self):
    print("\n" + "=" * 60)
    print("FINAL COMPREHENSIVE TEST")
    print("=" * 60)

    steps = [
        self.step1_register,
        self.step2_login,
        self.step3_get_products,
        self.step4_add_to_cart,
        self.step5_view_cart,
        self.step6_create_order,
        self.step7_view_orders,
    ]

    results = []
    for i, step in enumerate(steps, 1):
        try:
            success = step()
            results.append((i, success))
            if not success:
                print(f"\nStopping test due to failure at step {i}")
                break
        except Exception as e:
            print(f"✗ Error in step {i}: {e}")
            results.append((i, False))
            break

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for step_num, success in results:
        status = "✓" if success else "✗"
        print(f"{status} Step {step_num}")

    print(f"\nPassed: {passed}/{total}")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Your backend is working perfectly!")
        return True
    else:
        print(f"\n⚠ {total - passed} test(s) failed.")
        return False


if __name__ == "__main__":
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/api/products/products/", timeout=5)
        if response.status_code == 200:
            print("Server is running ✓")
            runner = TestRunner()
            runner.run()
        else:
            print(f"Server error: {response.status_code}")
    except Exception as e:
        print(f"Cannot connect to server: {e}")
        print("Please run: python manage.py runserver")
