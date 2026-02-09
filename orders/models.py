from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Order(models.Model):
    """Order model representing a customer's order"""

    class Status(models.TextChoices):
        NEW = "NEW", "New Order"
        CONFIRMED = "CONFIRMED", "Confirmed"
        PROCESSING = "PROCESSING", "Processing"
        SHIPPED = "SHIPPED", "Shipped"
        DELIVERED = "DELIVERED", "Delivered"
        CANCELLED = "CANCELLED", "Cancelled"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name="User",
    )

    # Order details
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
        verbose_name="Order Status",
    )

    # Contact information
    first_name = models.CharField(max_length=100, verbose_name="First Name")
    last_name = models.CharField(max_length=100, verbose_name="Last Name")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, verbose_name="Phone")

    # Delivery information
    address = models.TextField(verbose_name="Delivery Address")
    city = models.CharField(max_length=100, verbose_name="City")
    postal_code = models.CharField(max_length=20, verbose_name="Postal Code")
    country = models.CharField(max_length=100, verbose_name="Country")

    # Order totals
    subtotal = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Subtotal"
    )
    tax = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Tax"
    )
    shipping_cost = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Shipping Cost"
    )
    total = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Total Amount"
    )

    # Order metadata
    notes = models.TextField(blank=True, verbose_name="Order Notes")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")
    is_paid = models.BooleanField(default=False, verbose_name="Is Paid")
    payment_date = models.DateTimeField(
        null=True, blank=True, verbose_name="Payment Date"
    )

    # Delivery dates
    estimated_delivery = models.DateField(
        null=True, blank=True, verbose_name="Estimated Delivery"
    )
    delivered_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Delivered At"
    )

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.id} - {self.user.email} - {self.status}"

    def calculate_totals(self):
        """Calculate order totals from order items"""
        items = self.items.all()
        self.subtotal = sum(item.total_price for item in items)
        # Simple tax calculation (10%)
        self.tax = self.subtotal * Decimal("0.10")
        # Simple shipping calculation
        self.shipping_cost = (
            Decimal("10.00") if self.subtotal < Decimal("100.00") else Decimal("0.00")
        )
        self.total = self.subtotal + self.tax + self.shipping_cost
        self.save()

    def get_order_summary(self):
        """Get a summary of the order"""
        return {
            "order_id": self.id,
            "status": self.get_status_display(),
            "total": self.total,
            "item_count": self.items.count(),
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }


class OrderItem(models.Model):
    """Individual items within an order"""

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items", verbose_name="Order"
    )
    product = models.ForeignKey(
        "products.Product", on_delete=models.PROTECT, verbose_name="Product"
    )
    supplier_product = models.ForeignKey(
        "suppliers.SupplierProduct",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Supplier Product",
    )
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)], verbose_name="Quantity"
    )
    unit_price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Unit Price"
    )
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Total Price"
    )

    # Store product details at time of order (in case product changes later)
    product_name = models.CharField(
        max_length=200, verbose_name="Product Name (at order time)"
    )
    product_sku = models.CharField(
        max_length=100, blank=True, verbose_name="Product SKU"
    )

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"

    def __str__(self):
        return f"{self.quantity} x {self.product_name} (Order #{self.order.id})"

    def save(self, *args, **kwargs):
        """Calculate total price before saving"""
        if self.unit_price and self.quantity:
            self.total_price = self.unit_price * self.quantity
        if self.product and not self.product_name:
            self.product_name = self.product.name
        super().save(*args, **kwargs)
