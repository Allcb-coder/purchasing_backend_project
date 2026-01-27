from rest_framework import serializers
from .models import Cart, CartItem
from products.serializers import ProductSerializer
from products.models import Product
from suppliers.models import SupplierProduct
from suppliers.serializers import SupplierProductSerializer


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True
    )
    supplier_product = SupplierProductSerializer(read_only=True)
    supplier_product_id = serializers.PrimaryKeyRelatedField(
        queryset=SupplierProduct.objects.filter(is_available=True, supplier__accepts_orders=True),
        source='supplier_product',
        write_only=True,
        required=False,
        allow_null=True
    )
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    is_available = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = CartItem
        fields = [
            'id', 'cart', 'product', 'product_id', 'supplier_product', 'supplier_product_id',
            'quantity', 'unit_price', 'total_price', 'is_available', 'added_at', 'updated_at'
        ]
        read_only_fields = ['id', 'cart', 'unit_price', 'total_price', 'is_available', 'added_at', 'updated_at']
    
    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1")
        return value


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Cart
        fields = [
            'id', 'user', 'items', 'total_items', 'subtotal', 'total',
            'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'total_items', 'subtotal', 'total']
