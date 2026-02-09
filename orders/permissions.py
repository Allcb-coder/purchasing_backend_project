from rest_framework import permissions


class IsOrderOwner(permissions.BasePermission):
    """
    Permission to only allow order owner to access their orders.
    """

    def has_object_permission(self, request, view, obj):
        # Only the order owner can access their order
        return obj.user == request.user
