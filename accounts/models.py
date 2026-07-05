# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ('investor', 'Investor'),
        ('entrepreneur', 'Entrepreneur'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    bio = models.TextField(blank=True, default='')
    profile_picture = models.URLField(blank=True, default='')
    preferences = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.username} ({self.role})"
    
class StartupHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='startup_history')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    stage = models.CharField(max_length=50, blank=True)
    funding_needed = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class InvestmentHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='investment_history')
    startup_name = models.CharField(max_length=200)
    amount_invested = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)