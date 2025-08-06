from rest_framework import serializers

from .models import Flat

from ..users.serializers import UserSerializer

class FlatSerializer(serializers.ModelSerializer):
    members = UserSerializer(read_only=True, many=True)
    admins = UserSerializer(read_only=True, many=True)

    class Meta:
        model = Flat
        fields = ['id' ,'name', 'members', 'admins', 'can_member_edit_chores']
        read_only_fields = ['members', 'admins']
    
    # TODO make sure admin is also member otherwise don't let it work when saving maybe validate allows it or save()
