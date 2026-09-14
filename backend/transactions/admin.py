from django.contrib import admin
from .models import Merchant, Transaction

@admin.register(Merchant)
class MerchantAdmin(admin.ModelAdmin):
    list_display = ("merchant_id", "merchant_name", "category")
    search_fields = ("merchant_name", "merchant_id")

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("transaction_id", "account", "amount", "status", "timestamp", "location", "is_new_device")
    list_filter = ("status", "is_new_device")
    search_fields = ("transaction_id", "account__account_number", "location")
