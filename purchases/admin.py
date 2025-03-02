from django.contrib import admin
from .models import Purchase, PurchaseCategory

@admin.register(PurchaseCategory)
class PurchaseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'profile', 'created_at')
    list_filter = ('created_by', 'profile')
    search_fields = ('name', 'description')
    date_hierarchy = 'created_at'

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('title', 'amount', 'quantity', 'unit_price', 'vendor', 'category', 'status', 'date', 'payment_method', 'created_by', 'profile')
    list_filter = ('category', 'status', 'payment_method', 'created_by', 'profile', 'date')
    search_fields = ('title', 'description', 'vendor')
    date_hierarchy = 'date'
    readonly_fields = ('amount',)  # Since amount is calculated from quantity and unit_price
