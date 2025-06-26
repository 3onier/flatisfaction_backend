from rest_framework import permissions

class IsNotFlatMember(permissions.BasePermission):
     def has_object_permission(self, request, view, obj):
        flat = obj.flat
        user = request.user
        return len(flat.members.filter(username=user.username)) == 0 