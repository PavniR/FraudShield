from django.test import TestCase
from django.contrib.auth.models import User
from users.models import AccountProfile
from transactions.models import Transaction, Merchant
from fraud_detection.rule_engine import RuleEngine

class RuleEngineTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="rule_user", password="password123")
        self.profile = AccountProfile.objects.create(
            user=self.user,
            account_number="ACC-RULE-100",
            average_transaction_amount=2500.00,
            usual_location="Delhi",
            usual_device_id="DEV_PRIMARY"
        )
        self.merchant = Merchant.objects.create(merchant_id="M_AMAZON", merchant_name="Amazon")

    def test_legitimate_transaction_no_rules_triggered(self):
        tx = Transaction.objects.create(
            account=self.profile,
            merchant=self.merchant,
            amount=1500.00,
            location="Delhi",
            device_id="DEV_PRIMARY",
            is_new_device=False,
            recent_transaction_count=1
        )
        score, violations = RuleEngine.evaluate(tx, self.profile)
        self.assertEqual(len(violations), 0)
        self.assertEqual(score, 0.0)

    def test_unusually_high_amount_rule_triggered(self):
        tx = Transaction.objects.create(
            account=self.profile,
            merchant=self.merchant,
            amount=10000.00,  # 4x avg
            location="Delhi",
            device_id="DEV_PRIMARY",
            is_new_device=False,
            recent_transaction_count=1
        )
        score, violations = RuleEngine.evaluate(tx, self.profile)
        self.assertTrue(any(v["rule_name"] == "UNUSUALLY_HIGH_AMOUNT" for v in violations))
        self.assertGreaterEqual(score, 30.0)

    def test_multiple_rules_triggered(self):
        tx = Transaction.objects.create(
            account=self.profile,
            merchant=self.merchant,
            amount=75000.00,  # High amount
            location="Mumbai",  # Location mismatch
            device_id="DEV_NEW_123",
            is_new_device=True,  # New device
            recent_transaction_count=6  # High frequency
        )
        score, violations = RuleEngine.evaluate(tx, self.profile)
        self.assertGreaterEqual(len(violations), 3)
        self.assertGreaterEqual(score, 70.0)
