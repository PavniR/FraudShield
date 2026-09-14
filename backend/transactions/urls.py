from django.urls import path
from .views import TransactionListCreateView, TransactionDetailView, EvaluateTransactionView

urlpatterns = [
    path("", TransactionListCreateView.as_view(), name="transaction-list-create"),
    path("<int:pk>/", TransactionDetailView.as_view(), name="transaction-detail"),
    path("<int:pk>/evaluate/", EvaluateTransactionView.as_view(), name="transaction-evaluate"),
]
