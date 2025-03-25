from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import (
    Contact, 
    Email, 
    Event, 
    Notification, 
    WhatsAppMessage, 
    TelegramMessage,
    EmailAccount,
    EmailAttachment
)

# Register your models here.

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """Admin configuration for Contact model"""
    list_display = (
        'first_name', 
        'last_name', 
        'email', 
        'phone_number', 
        'messenger_type', 
        'company'
    )
    search_fields = (
        'first_name', 
        'last_name', 
        'email', 
        'phone_number', 
        'company'
    )
    list_filter = (
        'messenger_type', 
        'company'
    )
    ordering = ('last_name', 'first_name')

@admin.register(EmailAccount)
class EmailAccountAdmin(admin.ModelAdmin):
    list_display = ('email', 'provider', 'is_primary', 'is_active')
    search_fields = ('email', 'username')
    list_filter = ('provider', 'is_primary', 'is_active')

@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    """Admin configuration for Email model"""
    list_display = (
        'subject', 
        'sender', 
        'get_recipient', 
        'sent_at', 
        'is_read'
    )
    search_fields = (
        'subject', 
        'body', 
        'sender__email', 
        'recipient__email'
    )
    list_filter = (
        'is_read', 
        'sent_at'
    )
    ordering = ('-sent_at',)

    def get_recipient(self, obj):
        """Get recipient email for display"""
        return obj.recipient.email if obj.recipient else 'N/A'
    get_recipient.short_description = 'Recipient'

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """Admin configuration for Event model"""
    list_display = (
        'title', 
        'start_time', 
        'end_time', 
        'location', 
        'recurrence_type'
    )
    search_fields = (
        'title', 
        'description', 
        'location'
    )
    list_filter = (
        'start_time', 
        'end_time', 
        'recurrence_type'
    )
    ordering = ('-start_time',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin configuration for Notification model"""
    list_display = (
        'title', 
        'user', 
        'notification_type', 
        'is_read', 
        'created_at'
    )
    search_fields = (
        'title', 
        'message', 
        'user__email'
    )
    list_filter = (
        'notification_type', 
        'is_read', 
        'created_at'
    )
    ordering = ('-created_at',)

@admin.register(WhatsAppMessage)
class WhatsAppMessageAdmin(admin.ModelAdmin):
    """Admin configuration for WhatsApp Message model"""
    list_display = (
        'contact', 
        'user', 
        'status', 
        'sent_at', 
        'created_at'
    )
    search_fields = (
        'message_text', 
        'contact__first_name', 
        'contact__last_name', 
        'contact__email'
    )
    list_filter = (
        'status', 
        'sent_at', 
        'created_at'
    )
    ordering = ('-created_at',)

@admin.register(TelegramMessage)
class TelegramMessageAdmin(admin.ModelAdmin):
    """Admin configuration for Telegram Message model"""
    list_display = (
        'contact', 
        'user', 
        'status', 
        'sent_at', 
        'created_at'
    )
    search_fields = (
        'message_text', 
        'contact__first_name', 
        'contact__last_name', 
        'contact__email'
    )
    list_filter = (
        'status', 
        'sent_at', 
        'created_at'
    )
    ordering = ('-created_at',)

@admin.register(EmailAttachment)
class EmailAttachmentAdmin(admin.ModelAdmin):
    """Admin configuration for Email Attachment model"""
    list_display = (
        'file_name', 
        'uploaded_at'
    )
    search_fields = ['file']
    list_filter = (
        'uploaded_at',
    )
    ordering = ('-uploaded_at',)

    def file_name(self, obj):
        """Return the filename for display"""
        return obj.file.name
    file_name.short_description = 'File Name'
