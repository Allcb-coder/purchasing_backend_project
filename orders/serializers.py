# orders/serializers.py
from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            'id', 'order', 'product', 'product_name',
            'quantity', 'unit_price', 'total_price', 'product_sku'
        ]
        read_only_fields = ['id', 'order', 'unit_price', 'total_price',
                            'product_name', 'product_sku']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'status', 'status_display',
            'first_name', 'last_name', 'email', 'phone',
            'address', 'city', 'postal_code', 'country',
            'subtotal', 'tax', 'shipping_cost', 'total',
            'notes', 'created_at', 'updated_at',
            'is_paid', 'payment_date', 'estimated_delivery',
            'delivered_at', 'items'
        ]
        read_only_fields = [
            'id', 'user', 'subtotal', 'tax', 'shipping_cost', 'total',
            'created_at', 'updated_at', 'payment_date', 'delivered_at'
        ]

    def create(self, validated_data):
        return Order.objects.create(**validated_data)


class OrderCreateSerializer(serializers.Serializer):
    """Serializer for creating orders from cart"""
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20)
    address = serializers.CharField()
    city = serializers.CharField(max_length=100)
    postal_code = serializers.CharField(max_length=20)
    country = serializers.CharField(max_length=100)
    notes = serializers.CharField(required=False, allow_blank=True)
    save_as_default_address = serializers.BooleanField(default=False)

    def validate_email(self, value):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if request.user.email != value:
                raise serializers.ValidationError("Email must match your account email")
        return value
