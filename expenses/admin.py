from django.contrib import admin
from .models import Expense, ExpenseCategory, RecurringExpense

@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'profile', 'created_at')
    list_filter = ('created_by', 'profile')
    search_fields = ('name', 'description')
    date_hierarchy = 'created_at'

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('title', 'amount', 'category', 'date', 'payment_method', 'created_by', 'profile')
    list_filter = ('category', 'payment_method', 'created_by', 'profile', 'date')
    search_fields = ('title', 'description')
    date_hierarchy = 'date'

@admin.register(RecurringExpense)
class RecurringExpenseAdmin(admin.ModelAdmin):
    list_display = ('title', 'amount', 'category', 'frequency', 'is_active', 'created_by', 'profile')
    list_filter = ('category', 'is_active', 'frequency', 'created_by', 'profile')
    search_fields = ('title', 'notes')
    date_hierarchy = 'created_at'
