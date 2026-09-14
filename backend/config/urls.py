"""
FraudShield Master URL Routing
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    
    # API Routes
    path("api/auth/", include("users.urls")),
    path("api/transactions/", include("transactions.urls")),
    path("api/fraud/", include("fraud_detection.urls")),
    path("api/dashboard/", include("dashboard.urls")),
    
    # Web Dashboard Views
    path("", include("dashboard.web_urls")),
]
