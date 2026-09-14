from django.urls import path
from .web_views import dashboard_home, transactions_view, evaluate_tester_view, login_register_view

urlpatterns = [
    path("", dashboard_home, name="web-dashboard"),
    path("transactions/", transactions_view, name="web-transactions"),
    path("tester/", evaluate_tester_view, name="web-tester"),
    path("login/", login_register_view, name="web-auth"),
]
