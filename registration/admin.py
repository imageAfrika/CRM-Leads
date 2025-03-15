from django.contrib import admin
from .models import PaymentMethod, SubscriptionPlan, Company, Subscription, PaymentTransaction  

# Register your models here.

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price_monthly', 'price_annually', 'is_active')
    list_editable = ('price_monthly', 'price_annually', 'is_active')
    search_fields = ('name', 'description')

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone_number', 'created_at')
    search_fields = ('name', 'email', 'phone_number')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('company', 'plan', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active', 'plan')
    search_fields = ('company__name', 'plan__name')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'account_name', 'account_number', 'is_active')
    list_editable = ('is_active',)
    search_fields = ('account_name', 'account_number')

@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ('company', 'amount', 'status', 'payment_date')
    list_filter = ('status', 'payment_date')
    search_fields = ('company__name', 'transaction_reference')
    readonly_fields = ('created_at', 'updated_at')
