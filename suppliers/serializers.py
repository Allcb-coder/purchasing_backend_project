from rest_framework import serializers
from .models import Supplier, SupplierProduct
from products.serializers import ProductSerializer
from products.models import Product


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = [
            'id', 'name', 'email', 'phone', 'address',
            'is_active', 'accepts_orders', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class SupplierProductSerializer(serializers.ModelSerializer):
    supplier = SupplierSerializer(read_only=True)
    supplier_id = serializers.PrimaryKeyRelatedField(
        queryset=Supplier.objects.all(),
        source='supplier',
        write_only=True
    )
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True
    )
    
    class Meta:
        model = SupplierProduct
        fields = [
            'id', 'supplier', 'supplier_id', 'product', 'product_id',
            'supplier_price', 'supplier_quantity', 'is_available'
        ]
        read_only_fields = ['id']
