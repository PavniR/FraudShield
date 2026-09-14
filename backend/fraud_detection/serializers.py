from rest_framework import serializers
from .models import FraudPrediction, RuleViolation

class RuleViolationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RuleViolation
        fields = ["id", "rule_name", "explanation", "severity", "created_at"]


class FraudPredictionSerializer(serializers.ModelSerializer):
    rule_violations = serializers.SerializerMethodNestedField if hasattr(serializers, "SerializerMethodNestedField") else serializers.SerializerMethodField()

    class Meta:
        model = FraudPrediction
        fields = [
            "id",
            "transaction",
            "fraud_probability",
            "risk_score",
            "risk_level",
            "decision",
            "model_version",
            "rule_violations",
            "created_at",
        ]

    def get_rule_violations(self, obj):
        violations = RuleViolation.objects.filter(transaction=obj.transaction)
        return RuleViolationSerializer(violations, many=True).data
