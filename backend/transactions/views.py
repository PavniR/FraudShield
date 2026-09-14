import logging
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from users.models import AccountProfile
from .models import Merchant, Transaction
from .serializers import TransactionSerializer, MerchantSerializer
from fraud_detection.models import FraudPrediction, RuleViolation
from fraud_detection.risk_scorer import RiskScoringEngine
from fraud_detection.serializers import FraudPredictionSerializer

logger = logging.getLogger(__name__)


class TransactionListCreateView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        queryset = Transaction.objects.all().order_by("-timestamp")

        # Filters
        tx_status = request.query_params.get("status")
        if tx_status:
            queryset = queryset.filter(status=tx_status.upper())

        account_num = request.query_params.get("account_number")
        if account_num:
            queryset = queryset.filter(account__account_number=account_num)

        serializer = TransactionSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = TransactionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        account_number = serializer.validated_data.get("account_number")
        amount = serializer.validated_data.get("amount")
        location = serializer.validated_data.get("location", "Delhi")
        device_id = serializer.validated_data.get("device_id", "DEV_DEFAULT_001")
        is_new_device = serializer.validated_data.get("is_new_device", False)
        recent_count = serializer.validated_data.get("recent_transaction_count", 1)
        merchant_name = serializer.validated_data.get("merchant_id_str", "Amazon India")

        # 1. Fetch or create account profile
        profile, created = AccountProfile.objects.get_or_create(
            account_number=account_number,
            defaults={
                "user": User.objects.first() or User.objects.create_user(username=f"user_{account_number}", password="password123"),
                "average_transaction_amount": 2500.00,
                "usual_location": "Delhi",
                "usual_device_id": "DEV_DEFAULT_001"
            }
        )

        # 2. Fetch or create merchant
        merchant, _ = Merchant.objects.get_or_create(
            merchant_id=merchant_name.upper().replace(" ", "_"),
            defaults={"merchant_name": merchant_name, "category": "Retail"}
        )

        # 3. Create initial pending transaction
        transaction = Transaction.objects.create(
            account=profile,
            merchant=merchant,
            amount=amount,
            location=location,
            device_id=device_id,
            is_new_device=is_new_device,
            recent_transaction_count=recent_count,
            status="PENDING"
        )
        logger.info(f"Transaction created: {transaction.transaction_id} for amount ₹{amount}")

        # 4. Evaluate Fraud Risk
        eval_result = RiskScoringEngine.evaluate_transaction(transaction, profile)

        # 5. Update transaction status
        transaction.status = eval_result["status"]
        transaction.save()

        # 6. Save FraudPrediction model record
        prediction = FraudPrediction.objects.create(
            transaction=transaction,
            fraud_probability=eval_result["fraud_probability"],
            risk_score=eval_result["risk_score"],
            risk_level=eval_result["risk_level"],
            decision=eval_result["decision"],
            model_version=eval_result["model_version"]
        )

        # 7. Save RuleViolations
        for rv in eval_result["rule_violations"]:
            RuleViolation.objects.create(
                transaction=transaction,
                rule_name=rv["rule_name"],
                explanation=rv["explanation"],
                severity=rv["severity"]
            )

        logger.info(f"Transaction evaluated: {transaction.transaction_id} -> Decision: {eval_result['decision']} Score: {eval_result['risk_score']}")

        response_data = TransactionSerializer(transaction).data
        response_data["evaluation"] = FraudPredictionSerializer(prediction).data

        return Response(response_data, status=status.HTTP_201_CREATED)


class TransactionDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        transaction = get_object_or_404(Transaction, pk=pk)
        serializer = TransactionSerializer(transaction)
        data = serializer.data

        prediction = getattr(transaction, "fraud_prediction", None)
        if prediction:
            data["evaluation"] = FraudPredictionSerializer(prediction).data
        else:
            data["evaluation"] = None

        return Response(data, status=status.HTTP_200_OK)


class EvaluateTransactionView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, pk):
        transaction = get_object_or_404(Transaction, pk=pk)
        profile = transaction.account

        eval_result = RiskScoringEngine.evaluate_transaction(transaction, profile)
        
        transaction.status = eval_result["status"]
        transaction.save()

        prediction, _ = FraudPrediction.objects.update_or_create(
            transaction=transaction,
            defaults={
                "fraud_probability": eval_result["fraud_probability"],
                "risk_score": eval_result["risk_score"],
                "risk_level": eval_result["risk_level"],
                "decision": eval_result["decision"],
                "model_version": eval_result["model_version"]
            }
        )

        # Re-create rule violations
        RuleViolation.objects.filter(transaction=transaction).delete()
        for rv in eval_result["rule_violations"]:
            RuleViolation.objects.create(
                transaction=transaction,
                rule_name=rv["rule_name"],
                explanation=rv["explanation"],
                severity=rv["severity"]
            )

        return Response({
            "message": "Transaction re-evaluated successfully",
            "transaction_id": transaction.transaction_id,
            "evaluation": FraudPredictionSerializer(prediction).data
        }, status=status.HTTP_200_OK)
