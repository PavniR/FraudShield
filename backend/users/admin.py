from django.contrib import admin
from .models import AccountProfile

@admin.register(AccountProfile)
class AccountProfileAdmin(admin.ModelAdmin):
    list_display = ("account_number", "user", "average_transaction_amount", "usual_location", "created_at")
    search_fields = ("account_number", "user__username", "usual_location")
