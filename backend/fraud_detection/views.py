from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import FraudPrediction
from .serializers import FraudPredictionSerializer

class FraudPredictionListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = FraudPredictionSerializer
    queryset = FraudPrediction.objects.all().order_by("-created_at")

class FraudPredictionDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = FraudPredictionSerializer
    queryset = FraudPrediction.objects.all()
    lookup_field = "pk"
