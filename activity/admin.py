from django.contrib import admin
from .models import Event,EventParticipant,ActivityParticipant

admin.site.register(Event)
admin.site.register(EventParticipant)
admin.site.register(ActivityParticipant)
