from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsPostOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            True if request.method in SAFE_METHODS
            else obj.author == request.user
        )
