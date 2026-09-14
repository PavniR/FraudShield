from rest_framework import serializers
from .models import Merchant, Transaction
from users.serializers import AccountProfileSerializer

class MerchantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Merchant
        fields = ["id", "merchant_id", "merchant_name", "category"]


class TransactionSerializer(serializers.ModelSerializer):
    account_detail = AccountProfileSerializer(source="account", read_only=True)
    merchant_detail = MerchantSerializer(source="merchant", read_only=True)
    merchant_id_str = serializers.CharField(write_only=True, required=False, allow_blank=True)
    account_number = serializers.CharField(write_only=True)

    class Meta:
        model = Transaction
        fields = [
            "id",
            "transaction_id",
            "account",
            "account_number",
            "account_detail",
            "merchant",
            "merchant_id_str",
            "merchant_detail",
            "amount",
            "timestamp",
            "location",
            "device_id",
            "is_new_device",
            "recent_transaction_count",
            "status",
        ]
        read_only_fields = ["transaction_id", "account", "merchant", "timestamp", "status"]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Transaction amount must be strictly greater than zero.")
        return value
