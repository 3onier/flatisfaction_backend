from datetime import date;

from django.db import models

from ..flat.models import Flat
from django.contrib.auth.models import User

from ..common.enums import WeekDays

class Chore(models.Model):
    FREQUENCY_CHOICES = {
        "once": 'once',
        "daily": 'daily',
        "weekly": 'weekly',
        "montly": 'monthly',
        "irregular": 'irregular'
    }

    name = models.CharField(max_length=250)
    description = models.CharField(blank=True)
    start_date = models.DateField(default=date.today)
    end_date = models.DateField(null=True)
    frequency = models.CharField(choices=FREQUENCY_CHOICES)
    frequency_gap = models.IntegerField(default=1)
    weekdays = models.JSONField(default="[]")
    effort = models.IntegerField(default=1)
    responsible_members = models.ManyToManyField(User, related_name="responsible_members")
    flat = models.ForeignKey(Flat, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.pk}: {self.name}"


class ChoreAppointment(models.Model):
    date = models.DateField(default=date.today())
    chore = models.ForeignKey(Chore, related_name="chore", on_delete=models.CASCADE)
    flat = models.ForeignKey(Flat, related_name="flat", on_delete=models.CASCADE)
    assigned_member = models.ForeignKey(User, related_name="assigned_member", on_delete=models.CASCADE)
    executor = models.ForeignKey(User, related_name="executor", default=None, blank=True, null=True, on_delete=models.CASCADE)
    
    def is_completed(self):
        return self.executor != None 
