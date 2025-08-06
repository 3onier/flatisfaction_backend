from .models import Chore, ChoreAppointment
from ..flat.models import Flat

from datetime import date, timedelta
from random import randint

from rest_framework import exceptions


cache = {}

class Schedule:
    
    chores: list[Chore] = []
    chore_appointments: list[ChoreAppointment] = []

    def __init__(self, flat: Flat, from_date:date = date.today(), to_date: date = None): 
        if not from_date:
            from_date = date.today()
        self.from_date = from_date

        if not to_date:
            to_date = from_date + timedelta(days=150)
        self.to_date = to_date
        self.flat = flat
        self.chores = list(Chore.objects.filter(flat=self.flat))
        self.chore_appointments = []
        if to_date < from_date:
            raise  exceptions.ParseError("from_date cannot be later then to_date")


    def generate(self):
        # get all the chores of the flat
        self.chores.sort(key=lambda e: e.effort, reverse=True)
        for chore in self.chores:
            if not self._is_chore_within_boundaries(chore):
                continue
            app = self._generate_from_chore(chore)
            if app:
                self.chore_appointments += app
        self._assign_to_members()
        # sort by date
        self.chore_appointments.sort(key=lambda e: e.date)
        # here crate a caching by random ID


    def clear_all(self):
        apps = ChoreAppointment.objects.filter(flat=self.flat, date__gte=date.today())
        apps.delete()

    def clear_time_span(self):
        apps = ChoreAppointment.objects.filter(flat=self.flat, date__gte=self.from_date, date__lte=self.to_date)
        apps.delete()


    def _generate_from_chore(self, chore: Chore):
        if chore.frequency == Chore.FREQUENCY_CHOICES['once']:
            return self._generate_once(chore)
        elif chore.frequency == Chore.FREQUENCY_CHOICES['daily']:
            return self._generate_daily(chore)
        elif chore.frequency == Chore.FREQUENCY_CHOICES['weekly']:
            return self._generate_weekly(chore)
    

    def _generate_once(self, chore: Chore):
        if not (self.from_date < chore.start_date < self.to_date):
            return
        appointment = ChoreAppointment()
        appointment.chore = chore
        appointment.date = chore.start_date
        return [appointment]


    def _generate_daily(self, chore: Chore):
        out: list = []
        start_date = max(chore.start_date, self.from_date)
        # TODO make shure that every 2nd day from start day from start
        end_date = self.to_date
        if (chore.end_date):
            end_date = min(chore.end_date, end_date)
        now = start_date
        while (now <= end_date):
            app = ChoreAppointment()
            app.date = now
            app.chore = chore   
            out.append(app)
            now += timedelta(days=chore.frequency_gap)
        return out


    def _generate_weekly(self, chore: Chore):
        out: list = []
        start_date = max(chore.start_date, self.from_date)
        # TODO make shure that every 2nd day from start day from start
        end_date = self.to_date
        if (chore.end_date):
            end_date = min(chore.end_date, end_date)
        start_week = start_date.isocalendar().year * start_date.isocalendar().week
        week = lambda x : (x.isocalendar().year * x.isocalendar().week - start_week)
        now = start_date
        while (now <= end_date):
            if now.weekday() in chore.weekdays and week(now) % chore.frequency_gap == 0:
                app = ChoreAppointment()
                app.chore = chore
                app.date = now
                out.append(app)
            now += timedelta(days=1)
        return out


    def _assign_to_members(self):
        flat_members = self.flat.members.all()
        workload = {}
        for flat_member in flat_members:
            workload[flat_member.username] = 0
        # sort by effoert and within effoert within date
        self.chore_appointments.sort(key=lambda e: (-e.chore.effort, e.date))
        for app in self.chore_appointments:
            effort = app.chore.effort
            member_username_list = list(map(lambda x: x.username, app.chore.responsible_members.all()))
            member_with_least_point = min(member_username_list, key=lambda x: workload.get(x)) # TODO make only people who are assigned responsible 
            app.assigned_member = app.chore.responsible_members.get(username=member_with_least_point)
            workload[member_with_least_point] += effort

    def _is_chore_within_boundaries(self, chore: Chore):
        return True

    def save(self):
        """ Safes and overwrites the schedule selected in the time periode
        """
        def add_flat(app):
            app.flat = self.flat
            return app
        self.clear_time_span()
        self.chore_appointments = map(add_flat, self.chore_appointments)
        self.chore_appointments = ChoreAppointment.objects.bulk_create(self.chore_appointments)