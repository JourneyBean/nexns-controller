from rest_framework import permissions

class IsAuthenticatedClient(permissions.BasePermission):
    """
    Allow only authenticated clients.
    """

    def has_permission(self, request, view):
        return not not (hasattr(request, 'client') and request.client)
