from rest_framework import serializers

from products.models import Product
from products.serializers import ProductSerializer

from .models import Supplier, SupplierProduct


class SupplierProductSerializer(serializers.ModelSerializer):
    # Nested product info for read operations
    product = ProductSerializer(read_only=True)
    # For write operations (POST/PUT)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source="product", write_only=True
    )

    class Meta:
        model = SupplierProduct
        fields = [
            "id",
            "product",
            "product_id",
            "supplier_price",
            "supplier_quantity",
            "is_available",
        ]
        read_only_fields = ["id"]


class SupplierSerializer(serializers.ModelSerializer):
    # Include all products offered by this supplier
    supplier_products = SupplierProductSerializer(many=True, read_only=True)

    class Meta:
        model = Supplier
        fields = [
            "id",
            "name",
            "email",
            "phone",
            "address",
            "is_active",
            "accepts_orders",
            "created_at",
            "supplier_products",  # nested products
        ]
        read_only_fields = ["id", "created_at", "supplier_products"]
