
from rest_framework.permissions import BasePermission, SAFE_METHODS


class ReadOnly(BasePermission):
    """
    The request is authenticated as a user, or is a read-only request.
    """

    def has_permission(self, request, view):
        return bool(request.method in SAFE_METHODS)
