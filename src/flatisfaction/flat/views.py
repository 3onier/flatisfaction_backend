from rest_framework import generics, permissions, status, exceptions
from rest_framework.response import Response
from rest_framework.views import APIView

from django import shortcuts

from .models import Flat
from ..users.models import User

from .serializers import FlatSerializer
from ..users.serializers import UserSerializer

from .permissions import IsFlatMemberPermission, IsFlatAdminPermission, IsNotMemberOfAFlat

class FlatsView(generics.ListCreateAPIView):
    serializer_class = FlatSerializer

    def get_queryset(self):
        return Flat.objects.filter(members=self.request.user)

    def perform_create(self, serializer):
        serializer.save()
        flat = serializer.instance
        flat.members.add(self.request.user)
        flat.admins.add(self.request.user)
        flat.save()

class FlatView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Flat.objects.all()
    serializer_class = FlatSerializer
    permission_classes = [IsFlatAdminPermission|IsFlatMemberPermission]
    lookup_url_kwarg = "flat_id"


class FlatMembersView(generics.ListAPIView):
    """Get members of a Flat
        
        params:
        flat_id: int
        
    """
    serializer_class = UserSerializer
    permission_classes = [IsFlatAdminPermission|IsFlatMemberPermission]

    def get_queryset(self):
        flat_id = self.kwargs["flat_id"]
        flat = shortcuts.get_object_or_404(Flat, pk=flat_id)
        return flat.members.all()

class FlatMemberView(generics.RetrieveDestroyAPIView):
    """ Gets User which is member of the Flat
        DELETE will remove the user from the Flat as memeber and as admin

        params:
        flat_id: int
        user_id: int
    """
    serializer_class = UserSerializer
    permission_classes = [IsFlatAdminPermission|IsFlatMemberPermission]
    lookup_url_kwarg = 'user_id'
    
    def get_queryset(self):
        flat_id = self.kwargs["flat_id"]
        flat = shortcuts.get_object_or_404(Flat, pk=flat_id)
        return flat.members.all()

    def perform_destroy(self, user):
        flat = shortcuts.get_object_or_404(Flat, pk=self.kwargs.get('flat_id'))
        flat.members.remove(user)
        flat.admins.remove(user)
        flat.save()

class FlatAdminsView(generics.ListAPIView):
    """Get members of a Flat
        
        params:
        flat_id: int
        
    """
    serializer_class = UserSerializer
    permission_classes = [IsFlatAdminPermission|IsFlatMemberPermission]

    def get_queryset(self):
        flat_id = self.kwargs["flat_id"]
        flat = shortcuts.get_object_or_404(Flat, pk=flat_id)
        return flat.admins.all()

class FlatAdminView(generics.RetrieveDestroyAPIView):
    """ Gets User which is admin of the Flat
        DELETE will remove the user from the Flat as admin

        params:
        flat_id: int
    """
    serializer_class = UserSerializer
    permission_classes = [IsFlatAdminPermission|IsFlatMemberPermission]
    lookup_url_kwarg = 'user_id'
    
    def get_queryset(self):
        flat_id = self.kwargs["flat_id"]
        flat = shortcuts.get_object_or_404(Flat, pk=flat_id)
        return flat.admins.all()

    def perform_destroy(self, user):
        flat = shortcuts.get_object_or_404(Flat, pk=self.kwargs.get('flat_id'))
        flat.admins.remove(user)
        flat.save()

class MakeAdminView(APIView):
    permission_classes = [IsFlatAdminPermission]

    def get(self, request, flat_id, user_id):
        flat = shortcuts.get_object_or_404(Flat, pk=flat_id)
        user = shortcuts.get_object_or_404(flat.members.all(), pk=user_id)
        flat.admins.add(user)
        flat.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class LeaveFlat(APIView):
    permission_classes = [IsFlatMemberPermission]

    def delete_flat(self, flat: Flat):
        flat.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def make_all_members_admin(self, flat: Flat):
        flat.admins.set(flat.members.all())

    def get(self, request, flat_id=None, format=None):
        flat: Flat = shortcuts.get_object_or_404(Flat, pk=flat_id)
        # test how many members the flat has
        if len(flat.members.all()) == 1:
            return self.delete_flat(flat)
        flat.members.remove(request.user)
        flat.admins.remove(request.user)

        if len(flat.admins.all()) == 0:
            self.make_all_members_admin(flat)

        return Response(status=status.HTTP_204_NO_CONTENT)

