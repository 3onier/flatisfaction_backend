from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response

from django import shortcuts

from .models import Invite
from ..flat.models import Flat

from .serializers import InviteSerializer
from ..flat.serializers import FlatSerializer

from .permissions import IsNotFlatMember
from ..flat.permissions import IsFlatAdminPermission


class ListAndCreateInviteView(generics.ListCreateAPIView):
    """ Get the List
        
    """
    serializer_class = InviteSerializer
    permission_classes = [IsFlatAdminPermission]

    def get_queryset(self):
        flat_id = self.kwargs.get("flat_id")
        flat = shortcuts.get_object_or_404(Flat, pk=flat_id)
        return Invite.objects.filter(flat=flat)

    def perform_create(self, serializer):
        flat_id = self.kwargs.get("flat_id")
        flat = shortcuts.get_object_or_404(Flat, pk=flat_id)
        serializer.save(flat=flat)

class RetrieveDestroyInvite(generics.RetrieveDestroyAPIView):
    serializer_class = InviteSerializer
    permission_classes = [IsFlatAdminPermission]
    lookup_field = 'code'
    lookup_url_kwarg = 'invite_code'

    def get_queryset(self):
        flat_id = self.kwargs.get("flat_id")
        flat: Flat = shortcuts.get_object_or_404(Flat, pk=flat_id)
        return Invite.objects.filter(flat=flat)

class PublicInviteView(generics.RetrieveAPIView):
    """
        Get the Invite and the Flat by the invite code
    """
    queryset = Invite.objects.all()
    lookup_field = 'code'
    lookup_url_kwarg = 'invite_code'
    serializer_class = InviteSerializer
    permission_classes = [IsNotFlatMember]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        # check if is experired
        if instance.is_expired():
            return Response(status=status.HTTP_410_GONE)
        return Response(serializer.data)

class OpenInviteView(APIView):

    def get(self, request, format=None, invite_code=None):
        # get the invite
        invite = shortcuts.get_object_or_404(Invite, code=invite_code)
        if invite.is_expired():
            return Response(status=status.HTTP_410_GONE)
        invite.uses += 1
        invite.flat.members.add(request.user)
        invite.save()
        flat = invite.flat
        flat_serializer = FlatSerializer(flat)
        return Response(flat_serializer.data)

