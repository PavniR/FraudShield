from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from users.models import AccountProfile

class APIEndpointsTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="api_user", password="password123")
        self.profile = AccountProfile.objects.create(
            user=self.user,
            account_number="ACC-API-999",
            average_transaction_amount=2500.00,
            usual_location="Delhi"
        )

    def test_create_transaction_endpoint(self):
        payload = {
            "account_number": "ACC-API-999",
            "amount": 72500.00,
            "location": "Delhi",
            "device_id": "DEV_NEW_99",
            "is_new_device": True,
            "recent_transaction_count": 5,
            "merchant_id_str": "Amazon India"
        }
        response = self.client.post("/api/transactions/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("evaluation", response.data)
        self.assertIn("risk_score", response.data["evaluation"])
        self.assertIn(response.data["status"], ["REVIEW", "BLOCKED"])

    def test_invalid_amount_validation(self):
        payload = {
            "account_number": "ACC-API-999",
            "amount": -50.00,
            "location": "Delhi"
        }
        response = self.client.post("/api/transactions/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_dashboard_summary_endpoint(self):
        response = self.client.get("/api/dashboard/summary/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("kpis", response.data)
        self.assertIn("total_transactions", response.data["kpis"])
