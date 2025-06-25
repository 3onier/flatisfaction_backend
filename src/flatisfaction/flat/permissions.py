from rest_framework import permissions, exceptions

from django import shortcuts

from .models import Flat

class IsFlatMemberPermission(permissions.BasePermission):
    """ Check if user is member of the the flat
    """

    def has_permission(self, request, view):
        # try if view has flat_id given
        flat_id =  view.kwargs.get("flat_id")
        if flat_id is None:
            return True
        flat = shortcuts.get_object_or_404(Flat, pk=flat_id)
        return self.has_object_permission(request, view, flat)

    def has_object_permission(self, request, view, obj: Flat):
        if(not request.method in permissions.SAFE_METHODS):
            return False
        flat = shortcuts.get_object_or_404(Flat, pk=view.kwargs.get("flat_id"))
        if(flat.members.all().filter(username=request.user.username).first()):
            return True
        return False

class IsFlatAdminPermission(permissions.BasePermission):
    """ Check if user is admin of the Flat
    """

    def has_permission(self, request, view):
        # try if view has flat_id given
        flat_id =  view.kwargs.get("flat_id")
        if flat_id is None:
            return True
        flat = shortcuts.get_object_or_404(Flat, pk=flat_id)
        return self.has_object_permission(request, view, flat)

    def has_object_permission(self, request, view, obj):
        flat = shortcuts.get_object_or_404(Flat, pk=view.kwargs.get("flat_id"))
        if(flat.admins.all().filter(username=request.user.username).first()):
            return True
        return False

class IsNotMemberOfAFlat(permissions.BasePermission):
    """ Check if User is a member of a Flat so far

    """

    def has_permission(self, request, view):
        flats = Flat.objects.filter(
            members=request.user
        )
        return len(flats) == 0