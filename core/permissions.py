from rest_framework import permissions


class IsOwnerOrStaff(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Allow access only to the owner of the object or admin users
        if request.user and request.user.is_staff:
            return True
        return obj.owner == request.user
