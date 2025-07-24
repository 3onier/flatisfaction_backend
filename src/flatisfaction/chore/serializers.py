from rest_framework import serializers

from .models import Chore, ChoreAppointment

from ..users.serializers import UserSerializer
from..flat.serializers import FlatSerializer

class ChoreSerializer(serializers.ModelSerializer):
    responsible_members_verbose = UserSerializer(many=True, read_only=True, source="responsible_members")
    flat_verbose = FlatSerializer(read_only=True, source="flat")
    class Meta:
        model = Chore
        fields = "__all__"
        read_only = ["flat"]


class ChoreAppointmentSerializer(serializers.ModelSerializer):
    flat_verbose = FlatSerializer(source="flat", read_only=True)
    chore_verbose = ChoreSerializer(source="chore", read_only=True)
    executor_verbose = UserSerializer(source="executor", read_only=True)
    assigned_member_verbose = UserSerializer(source="assigned_member", read_only=True)
    is_completed = serializers.BooleanField()
    date = serializers.DateField(read_only=True) # format='%Y-%m-%dT00:00:00.000Z'
    class Meta:
        model = ChoreAppointment
        fields = "__all__"
        read_only = ["flat", 'date']

