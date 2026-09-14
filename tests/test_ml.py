from django.test import TestCase
from django.contrib.auth.models import User
from users.models import AccountProfile
from transactions.models import Transaction, Merchant
from fraud_detection.ml_service import MLFraudDetector
from fraud_detection.risk_scorer import RiskScoringEngine

class MLRiskScorerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="ml_user", password="password123")
        self.profile = AccountProfile.objects.create(
            user=self.user,
            account_number="ACC-ML-200",
            average_transaction_amount=2500.00,
            usual_location="Delhi",
            usual_device_id="DEV_ML"
        )
        self.merchant = Merchant.objects.create(merchant_id="M_FLIPKART", merchant_name="Flipkart")

    def test_ml_prediction_returns_float(self):
        tx = Transaction.objects.create(
            account=self.profile,
            merchant=self.merchant,
            amount=2000.00,
            location="Delhi",
            device_id="DEV_ML",
            is_new_device=False,
            recent_transaction_count=1
        )
        detector = MLFraudDetector.get_instance()
        prob = detector.predict_fraud_probability(tx, self.profile)
        self.assertIsInstance(prob, float)
        self.assertGreaterEqual(prob, 0.0)
        self.assertLessEqual(prob, 1.0)

    def test_risk_scorer_decision_mapping(self):
        # High risk transaction
        tx_high = Transaction.objects.create(
            account=self.profile,
            merchant=self.merchant,
            amount=85000.00,
            location="Bangalore",
            device_id="DEV_UNKNOWN",
            is_new_device=True,
            recent_transaction_count=8
        )
        result = RiskScoringEngine.evaluate_transaction(tx_high, self.profile)
        self.assertIn(result["decision"], ["REVIEW", "BLOCK"])
        self.assertIn(result["risk_level"], ["MEDIUM", "HIGH"])
        self.assertGreaterEqual(result["risk_score"], 35.0)
