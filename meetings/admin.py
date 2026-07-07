from django.contrib import admin
from .models import Meeting


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ['title', 'organizer', 'participant', 'start_time', 'end_time', 'status']
    list_filter = ['status']
    search_fields = ['title', 'organizer__email', 'participant__email']
