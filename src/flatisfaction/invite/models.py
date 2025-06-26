from django.db import models

from ..flat.models import Flat

import random

def generate_random_invite_string():
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890"
    return ''.join(random.choice(chars) for _ in range(10))

class Invite(models.Model):
    flat = models.ForeignKey(Flat, on_delete=models.CASCADE)
    code = models.CharField(max_length=10, default=generate_random_invite_string)
    max_uses = models.IntegerField(default=1)
    uses = models.IntegerField(default=0)

    def is_expired(self):
        return self.uses >= self.max_uses