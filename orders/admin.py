from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('unit_price', 'total_price', 'product_name')
    can_delete = False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total', 'is_paid', 'created_at')
    list_filter = ('status', 'is_paid', 'created_at', 'country')
    search_fields = ('user__email', 'first_name', 'last_name', 'email')
    readonly_fields = ('created_at', 'updated_at', 'subtotal', 'tax', 'shipping_cost', 'total')
    inlines = [OrderItemInline]
    actions = ['mark_as_paid', 'mark_as_shipped', 'mark_as_delivered']

    def mark_as_paid(self, request, queryset):
        queryset.update(is_paid=True, status='CONFIRMED')
    mark_as_paid.short_description = "Mark selected orders as paid"

    def mark_as_shipped(self, request, queryset):
        queryset.update(status='SHIPPED')
    mark_as_shipped.short_description = "Mark selected orders as shipped"

    def mark_as_delivered(self, request, queryset):
        queryset.update(status='DELIVERED')
    mark_as_delivered.short_description = "Mark selected orders as delivered"

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product_name', 'quantity', 'unit_price', 'total_price')
    list_filter = ('order__status',)
    search_fields = ('order__id', 'product_name')