import uuid
from django.db import models
from users.models import AccountProfile

class Merchant(models.Model):
    merchant_id = models.CharField(max_length=50, unique=True)
    merchant_name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, default="Retail")

    def __str__(self):
        return f"{self.merchant_name} ({self.category})"


class Transaction(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("ALLOWED", "Allowed"),
        ("REVIEW", "Under Review"),
        ("BLOCKED", "Blocked"),
    ]

    transaction_id = models.CharField(max_length=50, unique=True, default=uuid.uuid4, editable=False)
    account = models.ForeignKey(AccountProfile, on_delete=models.CASCADE, related_name="transactions")
    merchant = models.ForeignKey(Merchant, on_delete=models.SET_NULL, null=True, blank=True, related_name="transactions")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=100, default="Delhi")
    device_id = models.CharField(max_length=100, default="DEV_DEFAULT_001")
    is_new_device = models.BooleanField(default=False)
    recent_transaction_count = models.IntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")

    def __str__(self):
        return f"TX {self.transaction_id[:8]} - ₹{self.amount} ({self.status})"
