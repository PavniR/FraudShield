from django.contrib import admin
from .models import FraudPrediction, RuleViolation

@admin.register(FraudPrediction)
class FraudPredictionAdmin(admin.ModelAdmin):
    list_display = ("transaction", "fraud_probability", "risk_score", "risk_level", "decision", "created_at")
    list_filter = ("risk_level", "decision")
    search_fields = ("transaction__transaction_id",)

@admin.register(RuleViolation)
class RuleViolationAdmin(admin.ModelAdmin):
    list_display = ("transaction", "rule_name", "severity", "created_at")
    list_filter = ("severity", "rule_name")
