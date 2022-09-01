from rest_framework import permissions


class PostOwnerPerms(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, post):
        """
        Return `True` if permission is granted, `False` otherwise.
        """

        return request.user == post.user