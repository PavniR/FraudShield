"""
FraudShield Risk Scoring & Decision Engine
------------------------------------------
Combines Machine Learning fraud probability and Rule Engine violations into a composite
risk score (0 to 100) and maps it to actionable fraud decisions (ALLOW / REVIEW / BLOCK).
"""

from .rule_engine import RuleEngine
from .ml_service import MLFraudDetector


class RiskScoringEngine:
    """
    Risk Scoring Formula:
        ML Component Score (0-100) = ML Probability * 100
        Rule Component Score (0-100) = Rule Engine Total Score
        
        Final Risk Score = (ML Component Score * 0.60) + (Rule Component Score * 0.40)
    """

    @classmethod
    def evaluate_transaction(cls, transaction, account_profile):
        # 1. Run Rule Engine
        rule_score, rule_violations = RuleEngine.evaluate(transaction, account_profile)

        # 2. Run ML Fraud Detector
        ml_detector = MLFraudDetector.get_instance()
        ml_probability = ml_detector.predict_fraud_probability(transaction, account_profile)
        ml_score = ml_probability * 100.0

        # 3. Calculate Composite Risk Score (0-100)
        final_risk_score = round((ml_score * 0.60) + (rule_score * 0.40), 2)
        final_risk_score = max(0.0, min(100.0, final_risk_score))

        # 4. Map Risk Score to Decision & Risk Level
        if final_risk_score >= 70.0:
            decision = "BLOCK"
            risk_level = "HIGH"
            status = "BLOCKED"
        elif final_risk_score >= 35.0:
            decision = "REVIEW"
            risk_level = "MEDIUM"
            status = "REVIEW"
        else:
            decision = "ALLOW"
            risk_level = "LOW"
            status = "ALLOWED"

        return {
            "fraud_probability": round(ml_probability, 4),
            "risk_score": final_risk_score,
            "risk_level": risk_level,
            "decision": decision,
            "status": status,
            "rule_violations": rule_violations,
            "model_version": "RandomForest-v1.0"
        }
