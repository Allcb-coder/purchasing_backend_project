from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner
        return obj.user == request.user


class IsSupplierUser(permissions.BasePermission):
    """
    Allow access only to users with supplier profile.
    """
    def has_permission(self, request, view):
        return hasattr(request.user, 'profile') and request.user.profile.user_type == 'SUPPLIER'


class IsCustomerUser(permissions.BasePermission):
    """
    Allow access only to users with customer profile.
    """
    def has_permission(self, request, view):
        return hasattr(request.user, 'profile') and request.user.profile.user_type == 'CUSTOMER'