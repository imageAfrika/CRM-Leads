from django.contrib import admin
from .models import Client
from documents.models import Quote  # Import Quote from documents app
from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone']
    search_fields = ['name', 'email']
    list_filter = ['created_at']

# Remove or comment out the Quote registration since it should be in documents/admin.py
# @admin.register(Quote)
# class QuoteAdmin(admin.ModelAdmin):
#     list_display = ['client', 'quote_date', 'amount']
#     list_filter = ['quote_date', 'client']
#     search_fields = ['client__name', 'description']
#     date_hierarchy = 'quote_date'

class Command(BaseCommand):
    help = 'Create default user groups'

    def handle(self, *args, **kwargs):
        Group.objects.get_or_create(name='Staff')
        self.stdout.write('Successfully created Staff group')

