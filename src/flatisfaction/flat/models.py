from django.db import models

from django.contrib.auth.models import User

class Flat(models.Model):
    name = models.CharField(max_length=150)
    members = models.ManyToManyField(User, related_name='member_flats')
    admins = models.ManyToManyField(User, related_name='admin_flats')
