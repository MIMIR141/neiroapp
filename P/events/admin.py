from django.contrib import admin
from .models import Event, InviteLink, EventRegistration, Notification, UserProfile

admin.site.register(Event)
admin.site.register(InviteLink)
admin.site.register(EventRegistration)
admin.site.register(Notification)
admin.site.register(UserProfile)
