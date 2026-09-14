"""
FraudShield Rule Engine
-----------------------
Evaluates a transaction against deterministic heuristic rules based on account profile
and behavioral metrics.
"""

from decimal import Decimal


class RuleEngine:
    """
    Evaluates 5 core fraud detection rules and returns triggered violations and total rule score.
    """

    @staticmethod
    def evaluate(transaction, account_profile):
        violations = []
        rule_score = 0.0

        amount = Decimal(str(transaction.amount))
        avg_amount = Decimal(str(account_profile.average_transaction_amount))

        # Rule 1: Unusually High Amount (Amount > 3x Average)
        if avg_amount > 0 and amount > (avg_amount * Decimal("3.0")):
            violations.append({
                "rule_name": "UNUSUALLY_HIGH_AMOUNT",
                "explanation": f"Transaction amount (₹{amount:,.2f}) is significantly higher than user's average (₹{avg_amount:,.2f}).",
                "severity": "HIGH",
                "score": 30.0
            })
            rule_score += 30.0

        # Rule 2: New Device + Elevated Amount
        if transaction.is_new_device and amount > (avg_amount * Decimal("1.5")):
            violations.append({
                "rule_name": "NEW_DEVICE_HIGH_AMOUNT",
                "explanation": "Transaction originated from an unrecognized device with an elevated transaction amount.",
                "severity": "HIGH",
                "score": 25.0
            })
            rule_score += 25.0

        # Rule 3: High Transaction Frequency (Burst)
        if transaction.recent_transaction_count >= 5:
            violations.append({
                "rule_name": "HIGH_TRANSACTION_FREQUENCY",
                "explanation": f"High burst of recent transactions detected ({transaction.recent_transaction_count} in short window).",
                "severity": "MEDIUM",
                "score": 20.0
            })
            rule_score += 20.0

        # Rule 4: Unusual Transaction Hour (11 PM to 5 AM)
        hour = transaction.timestamp.hour if hasattr(transaction.timestamp, "hour") else 12
        if hour >= 23 or hour < 5:
            violations.append({
                "rule_name": "UNUSUAL_TRANSACTION_TIME",
                "explanation": f"Transaction initiated during unusual off-peak hours ({hour:02d}:00 hrs).",
                "severity": "LOW",
                "score": 10.0
            })
            rule_score += 10.0

        # Rule 5: Location Mismatch
        if transaction.location.strip().lower() != account_profile.usual_location.strip().lower():
            violations.append({
                "rule_name": "LOCATION_MISMATCH",
                "explanation": f"Transaction location ({transaction.location}) differs from user's primary location ({account_profile.usual_location}).",
                "severity": "MEDIUM",
                "score": 15.0
            })
            rule_score += 15.0

        # Clamp total rule score to max 100
        final_rule_score = min(rule_score, 100.0)
        return final_rule_score, violations
