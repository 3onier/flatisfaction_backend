from rest_framework import permissions
from rest_framework import request

from django import shortcuts

from .models import Chore, ChoreAppointment
from ..flat.models import Flat

from datetime import date

class IsFlatmemberAllowedToEditPermission(permissions.BasePermission):
    def has_permission(self, request: request.Request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if view.kwargs.get('flat_id'):
            flat = shortcuts.get_object_or_404(Flat, pk=view.kwargs.get('flat_id'))
            if flat.can_member_edit_chores and request.user in flat.members.all():
                return True
            return False
        return True

    def has_object_permission(self, request: request.Request, view, obj: Chore):
        # check if user is flatmember of the flat if not return False immediatially
        if obj.flat:
            flat = obj.flat
        else:
            flat = shortcuts.get_object_or_404(Flat, pk=view.kwargs.get('flat_id'))
        if len(flat.members.filter(username=request.user.username)) == 0:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return flat.can_member_edit_chores


class IsFlatAdminPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not view.kwargs.get('flat_id'):
            return True
        flat = shortcuts.get_object_or_404(Flat, pk=view.kwargs.get('flat_id'))
        if request.user in flat.admins.all():
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if obj.flat:    
            flat = obj.flat
        else:
            flat = shortcuts.get_object_or_404(Flat, pk=view.kwargs.get('flat_id'))
        return len(flat.admins.filter(username=request.user.username)) != 0

class IsFlatMemberPermission(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if not obj.flat:
            return False
        return len(obj.flat.members.filter(id=request.user.id).all()) != 0 
