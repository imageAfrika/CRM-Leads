from django.contrib import admin
from .models import Sale

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['client', 'sale_date', 'amount']
    list_filter = ['sale_date', 'client']
    search_fields = ['client__name', 'description']
    date_hierarchy = 'sale_date'

