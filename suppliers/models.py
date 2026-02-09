from django.core.validators import MinValueValidator
from django.db import models


class Supplier(models.Model):
    """Supplier/Shop model"""

    name = models.CharField(max_length=200, verbose_name="Supplier name")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Phone")
    address = models.TextField(verbose_name="Address")
    is_active = models.BooleanField(default=True, verbose_name="Is active")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")

    # Supplier can accept orders or not
    accepts_orders = models.BooleanField(default=True, verbose_name="Accepts orders")

    class Meta:
        verbose_name = "Supplier"
        verbose_name_plural = "Suppliers"
        ordering = ["name"]

    def __str__(self):
        return self.name


class SupplierProduct(models.Model):
    """Products offered by suppliers with supplier-specific pricing"""

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name="supplier_products",
        verbose_name="Supplier",
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="supplier_products",
        verbose_name="Product",
    )
    supplier_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Supplier price",
    )
    supplier_quantity = models.PositiveIntegerField(
        default=0, verbose_name="Supplier quantity"
    )
    is_available = models.BooleanField(default=True, verbose_name="Is available")

    class Meta:
        verbose_name = "Supplier Product"
        verbose_name_plural = "Supplier Products"
        unique_together = ["supplier", "product"]

    def __str__(self):
        return f"{self.supplier.name} - {self.product.name}"
