from rest_framework import views, generics, response, exceptions, status
from django import shortcuts
from django.db.models import Q

from django.core.cache import cache

from .models import Chore, ChoreAppointment
from ..flat.models import Flat

from .serializers import ChoreSerializer, ChoreAppointmentSerializer

from .permissions import IsFlatmemberAllowedToEditPermission, IsFlatAdminPermission, IsFlatMemberPermission

from .schedule import Schedule

from .exceptions import ChoreAppointmentConflict

from datetime import date


class ListAllUserChores(generics.ListAPIView):
    serializer_class = ChoreSerializer

    def get_queryset(self):
        flats = Flat.objects.filter(members=self.request.user)
        return Chore.objects.filter(flat__in=flats)

class RetrieveUpdateDestroyChore(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ChoreSerializer
    permission_classes = [IsFlatmemberAllowedToEditPermission|IsFlatAdminPermission]

    def get_queryset(self):
        flats = Flat.objects.filter(members=self.request.user)
        return Chore.objects.filter(flat__in=flats)

class ListCreateFlatChores(generics.ListCreateAPIView):
    serializer_class = ChoreSerializer
    permission_classes = [IsFlatmemberAllowedToEditPermission|IsFlatAdminPermission]

    def get_queryset(self):
        flat = shortcuts.get_object_or_404(Flat, pk=self.kwargs.get('flat_id'))
        return Chore.objects.filter(flat=flat)
    
    def perform_create(self, serializer):
        flat = shortcuts.get_object_or_404(Flat, pk=self.kwargs.get('flat_id'))
        new = serializer.save()
        new.flat = flat
        new.save()


class ListChoreAppointments(generics.ListAPIView):
    serializer_class = ChoreAppointmentSerializer
    permission_classes = [IsFlatAdminPermission|IsFlatmemberAllowedToEditPermission]

    def get_queryset(self):
        flat = shortcuts.get_object_or_404(Flat, pk=self.kwargs.get('flat_id'))
        appointments = ChoreAppointment.objects.filter(flat=flat)
        appointments = self._apply_date_filter(appointments)
        appointments = self._apply_user_filter(appointments)
        return appointments.order_by("date")

    def _apply_date_filter(self, appointments: ChoreAppointment):
        from_date = self.request.query_params.get('from')
        to_date = self.request.query_params.get('to')
        if (from_date):
            from_date = date.fromisoformat(from_date)
            appointments = appointments.filter(date__gte=from_date)
        if (to_date):
            to_date = date.fromisoformat(to_date)
            appointments = appointments.filter(date__lte=to_date)
        
        return appointments
    
    def _apply_user_filter(self, appointments: ChoreAppointment):
        if self.request.query_params.get('user'):
            user = self.request.query_params.get('user')
            appointments = appointments.filter(assigned_member_id=user)
        return appointments


class RetrieveUpdateDestroyChoreAppointment(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ChoreAppointmentSerializer
    permission_classes = [IsFlatAdminPermission|IsFlatMemberPermission]

    def get_queryset(self):
        user = self.request.user
        flats = Flat.objects.filter(members=user)
        return ChoreAppointment.objects.filter(flat__in=flats)

    def is_first_undone_chore_appointment_since_today(self, appointment):
        appointments = ChoreAppointment.objects.filter(
            flat=appointment.flat,
            chore=appointment.chore,
            date__gte=date.today(),
            date__lt=appointment.date,
        )
        is_completed_list = [e.is_completed() for e in appointments]
        if len(is_completed_list) == 0:
            return True
        are_all_app_completed = all(is_completed_list)
        return are_all_app_completed

    def is_last_undone_chore_appointment_since_itself(self, appointment: ChoreAppointment):
        appointments = ChoreAppointment.objects.filter(
            flat=appointment.flat,
            chore=appointment.chore,
            date__gt=appointment.date,
        )
        is_completed_list = [e.is_completed() for e in appointments]
        if len(is_completed_list) == 0:
            return True
        return not any(is_completed_list)

    def _checkForChoreApointmentsConflicts(self, appointment):
        """ Checks for conflicts of chore Appointments
            Returns true on conflicts
            Conflict is when
                - The ChoreAppointment is not the first not completed Choreappointment since today
                    Examlple: Today is Monday. Rubbish needs to be taken out daily. 
                        Marking Tuesday as completed while monday is not raises a conflict
                - The Chore appointment has completed appointments after itself
                    Example: Today is Monday. Rubbish needs to be done daily.
                        Today has been marked as done. yesterday not. Marking yesterday as done will be a conflict
        """
        return not self.is_first_undone_chore_appointment_since_today(appointment) \
            or not self.is_last_undone_chore_appointment_since_itself(appointment)

    def perform_update(self, serializer):
        # here check if the Executor is being changed
        if serializer.instance.executor != serializer.validated_data['executor']:
            if self._checkForChoreApointmentsConflicts(serializer.instance):
                raise ChoreAppointmentConflict()
        serializer.save()


class ScheduleCreateDeleteView(views.APIView):
    permission_classes = [IsFlatAdminPermission|IsFlatmemberAllowedToEditPermission]

    def _get_from_and_to_date(self, request):
        from_date = request.query_params.get('from')
        to_date = request.query_params.get('to')
        if (from_date):
            from_date = date.fromisoformat(from_date)
        if (to_date):
            to_date = date.fromisoformat(to_date)
        return (from_date, to_date)
    
    def _generate_schedule(self, flat_id=None):
        from_date, to_date = self._get_from_and_to_date(self.request)
        flat = shortcuts.get_object_or_404(Flat, pk=flat_id)
        schedule = Schedule(flat=flat, from_date=from_date, to_date=to_date)
        schedule.generate()
        return schedule

    def get(self, request, format=None, flat_id=None):
        schedule = self._generate_schedule(flat_id=flat_id)
        out = ChoreAppointmentSerializer(schedule.chore_appointments, many=True)
        return response.Response(out.data)

    def post(self, request, format=None, flat_id=None):
        schedule = self._generate_schedule(flat_id=flat_id)
        schedule.save()
        out = ChoreAppointmentSerializer(schedule.chore_appointments, many=True)
        return response.Response(out.data)

    def delete(self, request, format=None, flat_id=None):
        from_date, to_date = self._get_from_and_to_date(request)
        flat = shortcuts.get_object_or_404(Flat, pk=flat_id)
        schedule: Schedule = Schedule(flat=flat, from_date=from_date, to_date=to_date)
        if(from_date or to_date):
            schedule.clear_time_span()
        else:
            schedule.clear_all()
        return response.Response(status=status.HTTP_204_NO_CONTENT)