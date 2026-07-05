from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, StartupHistory, InvestmentHistory

admin.site.register(User, UserAdmin)
admin.site.register(StartupHistory)
admin.site.register(InvestmentHistory)