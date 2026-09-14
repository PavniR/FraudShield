from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from transactions.models import Transaction
from transactions.serializers import TransactionSerializer
from fraud_detection.models import FraudPrediction
from fraud_detection.serializers import FraudPredictionSerializer

class DashboardSummaryView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        total_tx = Transaction.objects.count()
        allowed_tx = Transaction.objects.filter(status="ALLOWED").count()
        review_tx = Transaction.objects.filter(status="REVIEW").count()
        blocked_tx = Transaction.objects.filter(status="BLOCKED").count()
        suspicious_tx = review_tx + blocked_tx

        fraud_rate = round((suspicious_tx / total_tx * 100.0), 2) if total_tx > 0 else 0.0

        # Recent suspicious transactions
        recent_suspicious = Transaction.objects.filter(status__in=["REVIEW", "BLOCKED"]).order_by("-timestamp")[:5]
        
        suspicious_data = []
        for tx in recent_suspicious:
            item = TransactionSerializer(tx).data
            prediction = getattr(tx, "fraud_prediction", None)
            if prediction:
                item["evaluation"] = FraudPredictionSerializer(prediction).data
            suspicious_data.append(item)

        return Response({
            "kpis": {
                "total_transactions": total_tx,
                "allowed_count": allowed_tx,
                "review_count": review_tx,
                "blocked_count": blocked_tx,
                "total_suspicious": suspicious_tx,
                "fraud_rate_percent": fraud_rate,
            },
            "recent_suspicious_transactions": suspicious_data
        }, status=status.HTTP_200_OK)
