from django.db import models
from transactions.models import Transaction

class FraudPrediction(models.Model):
    RISK_LEVEL_CHOICES = [
        ("LOW", "Low Risk"),
        ("MEDIUM", "Medium Risk"),
        ("HIGH", "High Risk"),
    ]

    DECISION_CHOICES = [
        ("ALLOW", "Allow"),
        ("REVIEW", "Review"),
        ("BLOCK", "Block"),
    ]

    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, related_name="fraud_prediction")
    fraud_probability = models.FloatField()
    risk_score = models.FloatField(default=0.0)
    risk_level = models.CharField(max_length=10, choices=RISK_LEVEL_CHOICES)
    decision = models.CharField(max_length=10, choices=DECISION_CHOICES)
    model_version = models.CharField(max_length=50, default="RandomForest-v1.0")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prediction {self.transaction.transaction_id[:8]} - {self.decision} ({self.risk_score} pts)"


class RuleViolation(models.Model):
    SEVERITY_CHOICES = [
        ("LOW", "Low Severity"),
        ("MEDIUM", "Medium Severity"),
        ("HIGH", "High Severity"),
    ]

    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name="rule_violations")
    rule_name = models.CharField(max_length=100)
    explanation = models.TextField()
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rule {self.rule_name} [{self.severity}] - TX {self.transaction.transaction_id[:8]}"
