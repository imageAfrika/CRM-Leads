from django.contrib import admin
from .models import Document, Quote

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['get_document_number', 'document_type', 'client', 'document_date', 'total_amount', 'status']
    list_filter = ['document_type', 'status', 'document_date']
    search_fields = ['client__name', 'description']
    date_hierarchy = 'document_date'

@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ['quote_number', 'client', 'created_at', 'total_amount', 'status']
    list_filter = ['status', 'created_at']
    search_fields = ['client__name', 'description']