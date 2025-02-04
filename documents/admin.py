from django.contrib import admin
from .models import Document, Quote

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'client', 'document_type', 'total_amount', 'document_date']
    list_filter = ['document_type', 'document_date', 'client']
    search_fields = ['title', 'client__name', 'description']
    date_hierarchy = 'document_date'

@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ['quote_number', 'client', 'total_amount', 'status', 'valid_until']
    list_filter = ['status', 'created_at', 'valid_until']
    search_fields = ['quote_number', 'client__name', 'description']
    date_hierarchy = 'created_at'