from django.db import models
from main.models import User

class Subscription(models.Model):
    id_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    is_frozen = models.BooleanField(default=False)
    remaining_days_at_freeze = models.IntegerField(null=True, blank=True)
    frozen_days_left = models.IntegerField(blank=True, null=True)
    freeze_date = models.DateField(blank=True, null=True)
    max_freeze_days = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} — {self.id_user.phone_number}"
