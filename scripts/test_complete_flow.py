import json
import sys
import time

import requests

BASE_URL = "http://127.0.0.1:8000"


class E2ETest:
    def __init__(self):
        self.token = None
        self.user_id = None
        self.cart_id = None
        self.order_id = None
        self.product_id = None
        self.username = None
        self.password = "TestPass123!"
        self.headers = {}

    def print_step(self, step_num, description):
        print(f"\n{'='*60}")
        print(f"STEP {step_num}: {description}")
        print("=" * 60)

    def register_user(self):
        self.print_step(1, "REGISTERING NEW USER")
        # Create unique username
        timestamp = int(time.time())
        self.username = f"customer_{timestamp}"

        user_data = {
            "username": self.username,
            "email": f"{self.username}@example.com",
            "password": self.password,
            "password2": self.password,
            "first_name": "John",
            "last_name": "Doe",
        }

        response = requests.post(f"{BASE_URL}/api/auth/register/", json=user_data)

        if response.status_code in [200, 201]:
            print("✓ User registered successfully")
            print(f"  Username: {self.username}")
            print(f"  Email: {user_data['email']}")
            return True
        else:
            print(f"✗ Registration failed: {response.status_code}")
            print(f"  Error: {response.text}")
            return False

    def login(self):
        self.print_step(2, "LOGGING IN")

        if not self.username:
            print("✗ No username available")
            return False

        login_data = {"username": self.username, "password": self.password}

        response = requests.post(f"{BASE_URL}/api/auth/login/", json=login_data)

        if response.status_code == 200:
            data = response.json()
            self.token = data.get("token")
            self.user_id = data.get("user_id")
            self.headers = {"Authorization": f"Token {self.token}"}

            print("✓ Login successful")
            print(f"  Token: {self.token[:30]}...")
            print(f"  User ID: {self.user_id}")
            return True
        else:
            print(f"✗ Login failed: {response.status_code}")
            print(f"  Error: {response.text}")
            return False

    def browse_products(self):
        self.print_step(3, "BROWSING PRODUCTS")

        # Get all products
        response = requests.get(f"{BASE_URL}/api/products/products/")

        if response.status_code == 200:
            products = response.json()
            if isinstance(products, dict) and "results" in products:
                products = products["results"]
            elif isinstance(products, dict) and "count" in products:
                products = products.get("results", [])

            print(
                f"✓ Found {len(products) if isinstance(products, list) else 'unknown'} products"
            )

            # Show first 3 products
            if products and len(products) > 0:
                print("\nSample Products:")
                for i, product in enumerate(products[:3]):
                    print(
                        f"  {i+1}. {product.get('name', 'N/A')} - ${product.get('price', 'N/A')}"
                    )

                # Save first product ID for cart test
                self.product_id = products[0].get("id")
                print(f"\n  Selected product ID for cart: {self.product_id}")
                return True
            else:
                print("✗ No products found in database")
                return False
        else:
            print(f"✗ Failed to get products: {response.status_code}")
            print(f"  Response: {response.text[:100]}")
            return False

    def add_to_cart(self):
        self.print_step(4, "ADDING ITEMS TO CART")

        if not self.product_id:
            print("✗ No product ID available")
            return False

        # Add item to cart
        cart_data = {"product_id": self.product_id, "quantity": 2}

        response = requests.post(
            f"{BASE_URL}/api/cart/add_item/", headers=self.headers, json=cart_data
        )

        if response.status_code == 200:
            print("✓ Item added to cart")
            cart_item = response.json()
            product_name = cart_item.get("product", {}).get("name", "Unknown")
            print(f"  Product: {product_name}")
            print(f"  Quantity: {cart_item.get('quantity', 'N/A')}")
            print(f"  Total Price: ${cart_item.get('total_price', 'N/A')}")
            return True
        else:
            print(f"✗ Failed to add to cart: {response.status_code}")
            print(f"  Error: {response.text}")
            return False

    def view_cart(self):
        self.print_step(5, "VIEWING CART")

        response = requests.get(f"{BASE_URL}/api/cart/", headers=self.headers)

        if response.status_code == 200:
            cart_data = response.json()

            # Handle different response formats
            if isinstance(cart_data, list) and len(cart_data) > 0:
                cart = cart_data[0]
            else:
                cart = cart_data

            print("✓ Cart retrieved successfully")
            print(f"  Cart ID: {cart.get('id', 'N/A')}")
            print(f"  Total Items: {cart.get('total_items', 0)}")
            print(f"  Subtotal: ${cart.get('subtotal', 0)}")
            print(f"  Total: ${cart.get('total', 0)}")

            # Show cart items
            items = cart.get("items", [])
            if items:
                print("\n  Cart Items:")
                for i, item in enumerate(items):
                    product_name = item.get("product", {}).get("name", "Unknown")
                    print(
                        f"    {i+1}. {product_name} - {item.get('quantity', 0)} x ${item.get('unit_price', 0)}"
                    )

            return True
        else:
            print(f"✗ Failed to get cart: {response.status_code}")
            print(f"  Error: {response.text}")
            return False

    def create_order(self):
        self.print_step(6, "CREATING ORDER FROM CART")

        order_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": f"{self.username}@example.com",
            "phone": "+1234567890",
            "address": "123 Main Street",
            "city": "New York",
            "postal_code": "10001",
            "country": "USA",
            "notes": "Please deliver after 5 PM",
            "save_as_default_address": True,
        }

        response = requests.post(
            f"{BASE_URL}/api/orders/", headers=self.headers, json=order_data
        )

        if response.status_code == 201:
            order = response.json()
            self.order_id = order.get("id")

            print("✓ Order created successfully!")
            print(f"  Order ID: {order.get('id', 'N/A')}")
            print(f"  Status: {order.get('status_display', 'N/A')}")
            print(f"  Total Amount: ${order.get('total', 'N/A')}")
            print(
                f"  Shipping Address: {order.get('address', 'N/A')}, {order.get('city', 'N/A')}"
            )

            # Show order items
            items = order.get("items", [])
            if items:
                print("\n  Order Items:")
                for i, item in enumerate(items):
                    print(
                        f"    {i+1}. {item.get('product_name', 'Unknown')} - {item.get('quantity', 0)} x ${item.get('unit_price', 0)}"
                    )

            return True
        else:
            print(f"✗ Failed to create order: {response.status_code}")
            print(f"  Error: {response.text}")
            return False

    def view_orders(self):
        self.print_step(7, "VIEWING ORDER HISTORY")

        response = requests.get(f"{BASE_URL}/api/orders/", headers=self.headers)

        if response.status_code == 200:
            orders = response.json()
            if isinstance(orders, dict) and "results" in orders:
                orders = orders["results"]
            elif isinstance(orders, dict) and "count" in orders:
                orders = orders.get("results", [])

            print(
                f"✓ Found {len(orders) if isinstance(orders, list) else 'unknown'} orders"
            )

            if orders and len(orders) > 0:
                print("\n  Recent Orders:")
                for i, order in enumerate(orders[:3]):
                    print(
                        f"    {i+1}. Order #{order.get('id', 'N/A')} - {order.get('status_display', 'N/A')} - ${order.get('total', 'N/A')}"
                    )

            return True
        else:
            print(f"✗ Failed to get orders: {response.status_code}")
            print(f"  Error: {response.text}")
            return False

    def run_full_test(self):
        print("\n" + "=" * 60)
        print("STARTING COMPLETE E2E TEST")
        print("=" * 60)

        steps = [
            (self.register_user, "User Registration"),
            (self.login, "User Login"),
            (self.browse_products, "Browse Products"),
            (self.add_to_cart, "Add to Cart"),
            (self.view_cart, "View Cart"),
            (self.create_order, "Create Order"),
            (self.view_orders, "View Order History"),
        ]

        success_count = 0
        failed_count = 0

        for method, description in steps:
            try:
                if method():
                    success_count += 1
                else:
                    failed_count += 1
                    # Optionally continue or break
                    # break
            except Exception as e:
                print(f"✗ Error in {description}: {str(e)}")
                failed_count += 1

        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"✓ Successful steps: {success_count}")
        print(f"✗ Failed steps: {failed_count}")
        print(f"Total steps attempted: {success_count + failed_count}")

        if failed_count == 0:
            print("\n🎉 ALL TESTS PASSED! Your backend is working correctly!")
        else:
            print("\n⚠ Some tests failed. Check the logs above for details.")

        return failed_count == 0


def quick_api_test():
    """Quick test of basic API endpoints"""
    print("\n" + "=" * 60)
    print("QUICK API TEST")
    print("=" * 60)

    # Test public endpoints
    endpoints = [
        ("GET", "/api/products/products/", "List Products"),
        ("GET", "/api/products/categories/", "List Categories"),
        ("GET", "/swagger/", "Swagger UI"),
        ("GET", "/redoc/", "ReDoc UI"),
        ("GET", "/admin/", "Admin Interface"),
    ]

    for method, endpoint, description in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}")
                status = response.status_code
                if status == 200:
                    print(f"✓ {description}: {status} OK")
                else:
                    print(f"✗ {description}: {status}")
        except Exception as e:
            print(f"✗ {description}: Error - {str(e)}")


if __name__ == "__main__":
    # First check if server is running
    try:
        response = requests.get(f"{BASE_URL}/api/products/products/", timeout=5)
        if response.status_code == 200:
            print("✓ Server is running and responding")

            # Run quick API test
            quick_api_test()

            # Ask if user wants to run full E2E test
            print("\n" + "=" * 60)
            run_full = input("Run full E2E test? (y/n): ").strip().lower()

            if run_full == "y":
                # Run full test
                test = E2ETest()
                test.run_full_test()
            else:
                print("Skipping full E2E test.")
        else:
            print(f"✗ Server returned status code: {response.status_code}")
            print("Make sure the server is running: python manage.py runserver")
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to server. Make sure it's running:")
        print("  python manage.py runserver")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        sys.exit(1)
