from rest_framework import permissions


class IsCartOwner(permissions.BasePermission):
    """
    Permission to only allow cart owner to access their cart.
    """
    def has_object_permission(self, request, view, obj):
        # Only the cart owner can access their cart
        return obj.user == request.user


class IsCartItemOwner(permissions.BasePermission):
    """
    Permission to only allow cart item owner to access their cart items.
    """
    def has_object_permission(self, request, view, obj):
        # Only the cart owner can access their cart items
        return obj.cart.user == request.user