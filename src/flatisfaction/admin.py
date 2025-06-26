from django.contrib import admin

from .users.models import UserProfile
from .flat.models import Flat
from .invite.models import Invite

# Register your models here.
admin.site.register(UserProfile)

admin.site.register(Flat)
admin.site.register(Invite)