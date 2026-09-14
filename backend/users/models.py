from django.db import models
from django.contrib.auth.models import User

class AccountProfile(models.Model):
    """
    AccountProfile stores baseline user metadata required for rule checking
    and fraud risk evaluation.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    account_number = models.CharField(max_length=20, unique=True)
    account_age_days = models.IntegerField(default=30)
    average_transaction_amount = models.DecimalField(max_digits=12, decimal_places=2, default=2500.00)
    usual_location = models.CharField(max_length=100, default="Delhi")
    usual_device_id = models.CharField(max_length=100, default="DEV_DEFAULT_001")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Account {self.account_number} ({self.user.username})"
