from rest_framework import serializers

from .models import Flat

from ..users.serializers import UserSerializer

class FlatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flat
        fields = ['id' ,'name', 'members', 'admins']
        read_only_fields = ['members', 'admins']
    
    # TODO make sure admin is also member otherwise don't let it work when saving maybe validate allows it or save()
