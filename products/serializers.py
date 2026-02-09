from rest_framework import serializers

from .models import Category, Product, ProductParameter


# Serializer for product parameters (configurable characteristics)
class ProductParameterSerializer(serializers.ModelSerializer):
    # 'name' comes from the related Parameter model
    name = serializers.CharField(source="parameter.name")

    class Meta:
        model = ProductParameter
        fields = (
            "name",
            "value",
        )  # exposed in API as [{"name": "...", "value": "..."}]


# Serializer for categories (nested in product)
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description"]
        read_only_fields = ["id"]


# Main Product serializer
class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)  # nested read-only
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source="category",  # maps to Product.category
        write_only=True,  # only used for POST/PUT
    )
    in_stock = serializers.BooleanField(read_only=True)  # computed property
    parameters = ProductParameterSerializer(
        many=True, read_only=True
    )  # includes all configurable parameters for the product

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "category",
            "category_id",
            "description",
            "price",
            "quantity",
            "image",
            "is_active",
            "in_stock",
            "created_at",
            "updated_at",
            "parameters",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "in_stock"]

    # Validators for price and quantity
    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative")
        return value

    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Quantity cannot be negative")
        return value
