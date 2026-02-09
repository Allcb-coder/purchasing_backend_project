#!/usr/bin/env python
import os
import django
from decimal import Decimal

# =========================
# Django setup
# =========================
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "purchasing_backend.settings")
django.setup()

# =========================
# Imports
# =========================
from django.contrib.auth.models import User
from products.models import Category, Product
from suppliers.models import Supplier, SupplierProduct
from cart.models import Cart, CartItem
from orders.models import Order, OrderItem
from django.core.mail import send_mail
from django.conf import settings

# =========================
# Clean database safely
# =========================
print("Cleaning database...")
OrderItem.objects.all().delete()
Order.objects.all().delete()
CartItem.objects.all().delete()
Cart.objects.all().delete()
SupplierProduct.objects.all().delete()
Supplier.objects.all().delete()
Product.objects.all().delete()
Category.objects.all().delete()
User.objects.all().delete()
print("Database cleaned.\n")

# =========================
# Create test data
# =========================
print("Creating test data...")

# User
user = User.objects.create_user(username="testuser", password="password123", email="test@example.com")

# Categories & Products
cat1 = Category.objects.create(name="Electronics", description="All electronic items")
prod1 = Product.objects.create(
    name="TCL 6-Series 55\" 4K UHD Smart TV",
    category=cat1,
    description="High quality smart TV",
    price=Decimal("699.99"),
    quantity=10
)

prod2 = Product.objects.create(
    name="Apple AirPods Pro",
    category=cat1,
    description="Noise-cancelling earbuds",
    price=Decimal("249.99"),
    quantity=20
)

# Supplier
supplier = Supplier.objects.create(
    name="Best Supplier",
    email="supplier@example.com",
    phone="+1234567890",
    address="123 Supplier Street",
    accepts_orders=True
)

# Supplier Products
SupplierProduct.objects.create(
    supplier=supplier,
    product=prod1,
    supplier_price=Decimal("650.00"),
    supplier_quantity=5,
    is_available=True
)

SupplierProduct.objects.create(
    supplier=supplier,
    product=prod2,
    supplier_price=Decimal("230.00"),
    supplier_quantity=10,
    is_available=True
)

# Cart
cart = Cart.objects.create(user=user)
CartItem.objects.create(cart=cart, product=prod1, quantity=1)
CartItem.objects.create(cart=cart, product=prod2, quantity=2)

print("Test data created.\n")

# =========================
# Create Order from Cart
# =========================
from orders.views import OrderListView
from rest_framework.test import APIRequestFactory

factory = APIRequestFactory()
request = factory.post(
    "/orders/",
    {
        "first_name": "John",
        "last_name": "Doe",
        "email": "test@example.com",
        "phone": "+123456789",
        "address": "456 Customer St",
        "city": "Testville",
        "postal_code": "12345",
        "country": "Testland",
        "notes": "Please deliver quickly",
    },
    format="json",
)
request.user = user

view = OrderListView.as_view()
response = view(request)
print("Order creation response status:", response.status_code)
print("Order data:", response.data)

# =========================
# Send test email
# =========================
print("\nSending test email (console backend)...")
send_mail(
    subject="Test Order Email",
    message="This is a test email for order notification.",
    from_email=settings.DEFAULT_FROM_EMAIL,
    recipient_list=[user.email, settings.ADMIN_EMAIL],
)
print("Email sent! Check the console output.\n")

print("Full flow test completed successfully!")
