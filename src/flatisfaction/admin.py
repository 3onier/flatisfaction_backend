from django.contrib import admin

from .users.models import UserProfile
from .flat.models import Flat
from .invite.models import Invite
from .chore.models import Chore, ChoreAppointment

# Register your models here.
admin.site.register(UserProfile)

admin.site.register(Flat)
admin.site.register(Invite)

class ChoreAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "flat"]

admin.site.register(Chore, ChoreAdmin)
admin.site.register(ChoreAppointment)