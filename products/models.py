from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Category(models.Model):
    """Product category/catalog"""

    name = models.CharField(max_length=100, unique=True, verbose_name="Category name")
    description = models.TextField(blank=True, verbose_name="Description")

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    """Product model"""

    name = models.CharField(max_length=200, verbose_name="Product name")
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name="Category",
    )
    description = models.TextField(blank=True, verbose_name="Description")
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Price",
    )
    quantity = models.PositiveIntegerField(default=0, verbose_name="Quantity in stock")
    image = models.ImageField(
        upload_to="products/", blank=True, null=True, verbose_name="Image"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated at")
    is_active = models.BooleanField(default=True, verbose_name="Is active")

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - ${self.price}"

    @property
    def in_stock(self):
        return self.quantity > 0


class Parameter(models.Model):
    """Configurable product characteristic (e.g. color, size, RAM)"""

    name = models.CharField(max_length=100, unique=True, verbose_name="Parameter name")

    class Meta:
        verbose_name = "Parameter"
        verbose_name_plural = "Parameters"
        ordering = ["name"]

    def __str__(self):
        return self.name


class ProductParameter(models.Model):
    """Value of a parameter for a specific product"""

    product = models.ForeignKey(
        Product,
        related_name="parameters",
        on_delete=models.CASCADE,
        verbose_name="Product",
    )
    parameter = models.ForeignKey(
        Parameter, on_delete=models.CASCADE, verbose_name="Parameter"
    )
    value = models.CharField(max_length=255, verbose_name="Value")

    class Meta:
        verbose_name = "Product parameter"
        verbose_name_plural = "Product parameters"
        unique_together = ("product", "parameter")

    def __str__(self):
        return f"{self.product.name}: {self.parameter.name} = {self.value}"
