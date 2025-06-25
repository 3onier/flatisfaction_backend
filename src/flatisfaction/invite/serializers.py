from rest_framework import serializers

from .models import Invite

from ..flat.serializers import FlatSerializer

class InviteSerializer(serializers.ModelSerializer):
    flat = FlatSerializer(read_only=True)
    class Meta:
        model = Invite
        fields = ['flat', 'code', 'max_uses', 'uses', 'is_expired']
        read_only_fields = ['flat', 'code', 'uses']