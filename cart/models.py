from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Cart(models.Model):
    """Shopping cart for a user"""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart",
        verbose_name="User",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")
    is_active = models.BooleanField(default=True, verbose_name="Is Active")

    class Meta:
        verbose_name = "Cart"
        verbose_name_plural = "Carts"

    def __str__(self):
        return f"Cart of {self.user.email}"

    @property
    def total_items(self):
        """Get total number of items in cart"""
        return self.items.count()

    @property
    def subtotal(self):
        """Calculate subtotal of all items in cart"""
        return sum(item.total_price for item in self.items.all())

    @property
    def total(self):
        """Calculate total with tax and shipping"""
        # Simple calculation for now
        return self.subtotal

    def clear(self):
        """Remove all items from cart"""
        self.items.all().delete()
        self.save()

    def merge_with_session_cart(self, session_cart_items):
        """Merge session cart items with user cart (for when user logs in)"""
        for session_item in session_cart_items:
            cart_item, created = self.items.get_or_create(
                product_id=session_item["product_id"],
                defaults={"quantity": session_item["quantity"]},
            )
            if not created:
                cart_item.quantity += session_item["quantity"]
                cart_item.save()


class CartItem(models.Model):
    """Individual items in the shopping cart"""

    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name="items", verbose_name="Cart"
    )
    product = models.ForeignKey(
        "products.Product", on_delete=models.CASCADE, verbose_name="Product"
    )
    supplier_product = models.ForeignKey(
        "suppliers.SupplierProduct",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Supplier Product",
    )
    quantity = models.PositiveIntegerField(
        default=1, validators=[MinValueValidator(1)], verbose_name="Quantity"
    )
    added_at = models.DateTimeField(auto_now_add=True, verbose_name="Added At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        verbose_name = "Cart Item"
        verbose_name_plural = "Cart Items"
        unique_together = ["cart", "product", "supplier_product"]

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def unit_price(self):
        """Get unit price from supplier or product"""
        if self.supplier_product:
            return self.supplier_product.supplier_price
        return self.product.price

    @property
    def total_price(self):
        """Calculate total price for this item"""
        return self.unit_price * self.quantity

    @property
    def is_available(self):
        """Check if item is available in stock"""
        if self.supplier_product:
            return (
                self.supplier_product.is_available
                and self.supplier_product.supplier_quantity >= self.quantity
            )
        return self.product.quantity >= self.quantity

    def save(self, *args, **kwargs):
        """Auto-select supplier product if not specified"""
        if self.product and not self.supplier_product:
            # Try to find an available supplier product
            supplier_product = self.product.supplier_products.filter(
                is_available=True, supplier__accepts_orders=True
            ).first()
            if supplier_product:
                self.supplier_product = supplier_product
        super().save(*args, **kwargs)
