import os

# Create products/serializers.py
products_serializers = '''from rest_framework import serializers
from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']
        read_only_fields = ['id']


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )
    in_stock = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'category', 'category_id', 
            'description', 'price', 'quantity', 'image',
            'is_active', 'in_stock', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'in_stock']
    
    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative")
        return value
    
    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Quantity cannot be negative")
        return value
'''

# Create suppliers/serializers.py
suppliers_serializers = '''from rest_framework import serializers
from .models import Supplier, SupplierProduct


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
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = SupplierProduct
        fields = [
            'id', 'supplier', 'supplier_id', 'product_name',
            'supplier_price', 'supplier_quantity', 'is_available'
        ]
        read_only_fields = ['id', 'product_name']
'''

# Create cart/serializers.py
cart_serializers = '''from rest_framework import serializers
from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(
        source='product.price', 
        max_digits=10, 
        decimal_places=2, 
        read_only=True
    )
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = CartItem
        fields = [
            'id', 'product_name', 'product_price', 'quantity', 
            'unit_price', 'total_price', 'added_at', 'updated_at'
        ]
        read_only_fields = ['id', 'product_name', 'product_price', 
                          'unit_price', 'total_price', 'added_at', 'updated_at']


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
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 
                          'total_items', 'subtotal', 'total']
'''

# Create cart/views.py
cart_views = '''from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from products.models import Product


class CartView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get user's cart"""
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    
    def post(self, request):
        """Add item to cart"""
        cart, created = Cart.objects.get_or_create(user=request.user)
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        
        if not product_id:
            return Response(
                {'error': 'product_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found or not active'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if item already in cart
        cart_item = CartItem.objects.filter(
            cart=cart,
            product=product
        ).first()
        
        if cart_item:
            cart_item.quantity += quantity
            cart_item.save()
        else:
            cart_item = CartItem.objects.create(
                cart=cart,
                product=product,
                quantity=quantity
            )
        
        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request):
        """Clear cart"""
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart.items.all().delete()
        return Response({'message': 'Cart cleared'}, status=status.HTTP_200_OK)


class CartItemView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def put(self, request, item_id):
        """Update cart item quantity"""
        try:
            cart_item = CartItem.objects.get(
                id=item_id,
                cart__user=request.user
            )
            
            quantity = request.data.get('quantity')
            if quantity is None:
                return Response(
                    {'error': 'quantity is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            quantity = int(quantity)
            if quantity <= 0:
                cart_item.delete()
                return Response(
                    {'message': 'Item removed from cart'},
                    status=status.HTTP_200_OK
                )
            
            cart_item.quantity = quantity
            cart_item.save()
            
            serializer = CartItemSerializer(cart_item)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except CartItem.DoesNotExist:
            return Response(
                {'error': 'Cart item not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    def delete(self, request, item_id):
        """Remove item from cart"""
        try:
            cart_item = CartItem.objects.get(
                id=item_id,
                cart__user=request.user
            )
            cart_item.delete()
            return Response(
                {'message': 'Item removed from cart'},
                status=status.HTTP_200_OK
            )
        except CartItem.DoesNotExist:
            return Response(
                {'error': 'Cart item not found'},
                status=status.HTTP_404_NOT_FOUND
            )
'''

# Create cart/urls.py
cart_urls = '''from django.urls import path
from . import views

urlpatterns = [
    path('', views.CartView.as_view(), name='cart'),
    path('items/<int:item_id>/', views.CartItemView.as_view(), name='cart-item'),
]
'''

# Write files
print("Creating fixed files...")

with open('products/serializers.py', 'w') as f:
    f.write(products_serializers)
print("✓ Created products/serializers.py")

with open('suppliers/serializers.py', 'w') as f:
    f.write(suppliers_serializers)
print("✓ Created suppliers/serializers.py")

with open('cart/serializers.py', 'w') as f:
    f.write(cart_serializers)
print("✓ Created cart/serializers.py")

with open('cart/views.py', 'w') as f:
    f.write(cart_views)
print("✓ Created cart/views.py")

with open('cart/urls.py', 'w') as f:
    f.write(cart_urls)
print("✓ Created cart/urls.py")

print("\nAll files created successfully!")
print("Now run: python manage.py check")
