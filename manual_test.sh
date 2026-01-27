#!/bin/bash

echo "=== Manual API Test ==="

# Register a user
echo "1. Registering user..."
REGISTER_RESPONSE=$(curl -s -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "manualtest",
    "email": "manual@test.com",
    "password": "ManualPass123!",
    "password2": "ManualPass123!",
    "first_name": "Manual",
    "last_name": "Test"
  }')

echo "Register response: $REGISTER_RESPONSE"

# Login
echo -e "\n2. Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "manualtest",
    "password": "ManualPass123!"
  }')

echo "Login response: $LOGIN_RESPONSE"

# Extract token
TOKEN=$(echo $LOGIN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['token'])")
echo "Token: $TOKEN"

# Get a product ID
echo -e "\n3. Getting product list..."
PRODUCTS_RESPONSE=$(curl -s "http://127.0.0.1:8000/api/products/products/")
PRODUCT_ID=$(echo $PRODUCTS_RESPONSE | python3 -c "
import sys, json
data = json.load(sys.stdin)
if 'results' in data and len(data['results']) > 0:
    print(data['results'][0]['id'])
else:
    print('0')
")

echo "First product ID: $PRODUCT_ID"

# Add to cart
echo -e "\n4. Adding to cart..."
CART_RESPONSE=$(curl -s -X POST http://127.0.0.1:8000/api/cart/add_item/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"product_id\": $PRODUCT_ID, \"quantity\": 1}")

echo "Cart response: $CART_RESPONSE"

# View cart
echo -e "\n5. Viewing cart..."
VIEW_CART=$(curl -s -X GET http://127.0.0.1:8000/api/cart/ \
  -H "Authorization: Token $TOKEN")

echo "Cart: $VIEW_CART"

# Create order
echo -e "\n6. Creating order..."
ORDER_RESPONSE=$(curl -s -X POST http://127.0.0.1:8000/api/orders/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Manual",
    "last_name": "Test",
    "email": "manual@test.com",
    "phone": "+1234567890",
    "address": "123 Test St",
    "city": "Test City",
    "postal_code": "12345",
    "country": "Testland",
    "notes": "Test order"
  }')

echo "Order response: $ORDER_RESPONSE"

echo -e "\n=== Test Complete ==="
