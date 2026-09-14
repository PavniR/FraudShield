from rest_framework import serializers
from django.contrib.auth.models import User
from .models import AccountProfile

class AccountProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountProfile
        fields = ["account_number", "account_age_days", "average_transaction_amount", "usual_location", "usual_device_id"]

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    account_number = serializers.CharField(write_only=True)
    average_transaction_amount = serializers.DecimalField(max_digits=12, decimal_places=2, default=2500.00, write_only=True)
    usual_location = serializers.CharField(default="Delhi", write_only=True)
    usual_device_id = serializers.CharField(default="DEV_DEFAULT_001", write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "account_number", "average_transaction_amount", "usual_location", "usual_device_id"]

    def create(self, validated_data):
        account_number = validated_data.pop("account_number")
        avg_amount = validated_data.pop("average_transaction_amount", 2500.00)
        usual_location = validated_data.pop("usual_location", "Delhi")
        usual_device = validated_data.pop("usual_device_id", "DEV_DEFAULT_001")

        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"]
        )

        AccountProfile.objects.create(
            user=user,
            account_number=account_number,
            average_transaction_amount=avg_amount,
            usual_location=usual_location,
            usual_device_id=usual_device
        )

        return user

class UserSerializer(serializers.ModelSerializer):
    profile = AccountProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "profile"]
