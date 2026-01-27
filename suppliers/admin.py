from django.contrib import admin
from .models import Supplier, SupplierProduct

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'is_active', 'accepts_orders', 'created_at')
    list_filter = ('is_active', 'accepts_orders')
    search_fields = ('name', 'email', 'address')
    list_editable = ('is_active', 'accepts_orders')

@admin.register(SupplierProduct)
class SupplierProductAdmin(admin.ModelAdmin):
    list_display = ('supplier', 'product', 'supplier_price', 'supplier_quantity', 'is_available')
    list_filter = ('supplier', 'is_available')
    search_fields = ('product__name', 'supplier__name')
    list_editable = ('supplier_price', 'supplier_quantity', 'is_available')