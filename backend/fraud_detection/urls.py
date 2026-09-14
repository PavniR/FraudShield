from django.urls import path
from .views import FraudPredictionListView, FraudPredictionDetailView

urlpatterns = [
    path("predictions/", FraudPredictionListView.as_view(), name="fraud-prediction-list"),
    path("predictions/<int:pk>/", FraudPredictionDetailView.as_view(), name="fraud-prediction-detail"),
]
