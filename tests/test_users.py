from django.test import TestCase
from django.contrib.auth.models import User
from users.models import AccountProfile

class UserAccountTestCase(TestCase):
    def test_create_user_and_profile(self):
        user = User.objects.create_user(username="testuser", password="password123")
        profile = AccountProfile.objects.create(
            user=user,
            account_number="ACC-TEST-001",
            average_transaction_amount=3000.00,
            usual_location="Delhi",
            usual_device_id="DEV_001"
        )
        self.assertEqual(profile.account_number, "ACC-TEST-001")
        self.assertEqual(profile.user.username, "testuser")
        self.assertEqual(float(profile.average_transaction_amount), 3000.00)
