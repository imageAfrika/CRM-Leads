from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import FileExtensionValidator
import uuid
from datetime import timedelta

# Create your models here.

class Contact(models.Model):
    """Contacts model for storing contact information"""
    MESSENGER_CHOICES = [
        ('whatsapp', 'WhatsApp'),
        ('telegram', 'Telegram'),
        ('signal', 'Signal'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='contacts')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    
    # Messenger details
    messenger_type = models.CharField(max_length=20, choices=MESSENGER_CHOICES, blank=True, null=True)
    messenger_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Additional details
    company = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name or ''}"

class EmailAccount(models.Model):
    """Email account configuration model"""
    PROVIDER_CHOICES = [
        ('gmail', 'Gmail'),
        ('telebird', 'Telebird'),
        ('yahoo', 'Yahoo'),
        ('custom', 'Custom SMTP'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='email_accounts')
    email = models.EmailField(unique=True)
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    
    # SMTP and IMAP settings
    smtp_host = models.CharField(max_length=255)
    smtp_port = models.IntegerField(default=587)
    imap_host = models.CharField(max_length=255)
    imap_port = models.IntegerField(default=993)
    
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)  # Encrypted in production
    
    is_primary = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.email

class EmailAttachment(models.Model):
    """Model to store email attachments"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(
        upload_to='email_attachments/%Y/%m/%d/',
        validators=[FileExtensionValidator(['pdf', 'doc', 'docx', 'jpg', 'png', 'txt', 'xlsx'])]
    )
    filename = models.CharField(max_length=255, blank=True)
    content_type = models.CharField(max_length=100, blank=True)
    file_size = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.filename and self.file:
            self.filename = self.file.name.split('/')[-1]
        if self.file and not self.file_size:
            self.file_size = self.file.size
        super().save(*args, **kwargs)

    def __str__(self):
        return self.filename or self.file.name

class Email(models.Model):
    """Email message model"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='sent_emails'
    )
    
    # For compatibility with the Telebird views, add these fields
    sender_name = models.CharField(max_length=255, blank=True)
    sender_email = models.EmailField(blank=True)
    
    # Replace single recipient with ManyToMany relationship
    recipients = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='received_emails',
        blank=True
    )
    
    # Add CC field
    cc = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='cc_emails',
        blank=True
    )
    
    subject = models.CharField(max_length=200)
    body = models.TextField()
    
    sent_at = models.DateTimeField(null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_read = models.BooleanField(default=False)
    is_draft = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    
    attachments = models.ManyToManyField(
        EmailAttachment, 
        related_name='emails', 
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.subject

class Event(models.Model):
    """Calendar event model with enhanced scheduling capabilities"""
    RECURRENCE_CHOICES = [
        ('none', 'No Repeat'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    
    PRIVACY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
        ('shared', 'Shared'),
    ]
    
    CATEGORY_CHOICES = [
        ('meeting', 'Meeting'),
        ('task', 'Task'),
        ('appointment', 'Appointment'),
        ('reminder', 'Reminder'),
        ('birthday', 'Birthday'),
        ('holiday', 'Holiday'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='events')
    
    # Add attendees field
    attendees = models.ManyToManyField(Contact, related_name='attended_events', blank=True)
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    
    location = models.CharField(max_length=300, blank=True, null=True)
    
    # Enhanced categorization and privacy
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    privacy = models.CharField(max_length=20, choices=PRIVACY_CHOICES, default='private')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    
    # Color coding for better visualization
    color = models.CharField(max_length=7, default='#007bff', help_text='Hex color code for event display')
    
    # Recurrence settings
    recurrence_type = models.CharField(max_length=20, choices=RECURRENCE_CHOICES, default='none')
    recurrence_interval = models.IntegerField(default=1)  # Every X days/weeks/months/years
    recurrence_end_date = models.DateField(null=True, blank=True)  # Optional end date for recurring events
    
    # Advanced notification settings
    send_email_reminder = models.BooleanField(default=True)
    send_sms_reminder = models.BooleanField(default=False)
    send_whatsapp_reminder = models.BooleanField(default=False)
    
    reminder_times = models.JSONField(
        default=list, 
        blank=True, 
        help_text='List of reminder times before the event (in minutes)'
    )
    
    # Attendees and sharing
    invited_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='invited_events')
    
    # External links or video conference details
    video_conference_link = models.URLField(blank=True, null=True)
    external_link = models.URLField(blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"
    
    def is_recurring(self):
        """Check if the event is a recurring event."""
        return self.recurrence_type != 'none'
    
    def get_next_occurrence(self):
        """Calculate the next occurrence of a recurring event."""
        if not self.is_recurring():
            return None
        
        # Implement logic to calculate next occurrence based on recurrence type
        # This is a placeholder and would need more complex implementation
        from dateutil.relativedelta import relativedelta
        
        if self.recurrence_type == 'daily':
            return self.start_time + timedelta(days=self.recurrence_interval)
        elif self.recurrence_type == 'weekly':
            return self.start_time + timedelta(weeks=self.recurrence_interval)
        elif self.recurrence_type == 'monthly':
            return self.start_time + relativedelta(months=self.recurrence_interval)
        elif self.recurrence_type == 'yearly':
            return self.start_time + relativedelta(years=self.recurrence_interval)
        
        return None

class Notification(models.Model):
    """Notification model for events and emails"""
    NOTIFICATION_TYPES = [
        ('event_reminder', 'Event Reminder'),
        ('email', 'Email'),
        ('system', 'System'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    
    is_read = models.BooleanField(default=False)
    related_object_id = models.UUIDField(null=True, blank=True)  # Link to Event or Email
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class WhatsAppMessage(models.Model):
    """WhatsApp messaging model"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='whatsapp_messages')
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='whatsapp_messages')
    
    message_text = models.TextField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Optional media attachments
    media_file = models.FileField(
        upload_to='whatsapp_media/%Y/%m/%d/',
        blank=True, 
        null=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif', 'pdf', 'doc', 'docx'])]
    )
    
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"WhatsApp Message to {self.contact.first_name} - {self.sent_at}"

class TelegramMessage(models.Model):
    """Telegram messaging model"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='telegram_messages')
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='telegram_messages')
    
    message_text = models.TextField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Optional media attachments
    media_file = models.FileField(
        upload_to='telegram_media/%Y/%m/%d/',
        blank=True, 
        null=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif', 'pdf', 'doc', 'docx'])]
    )
    
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Telegram Message to {self.contact.first_name} - {self.sent_at}"

class UserPreference(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='preferences')
    
    # Email preferences
    EMAIL_INTERFACE_CHOICES = [
        ('basic', 'Basic'),
        ('telebird', 'Telebird'),
    ]
    
    default_email_interface = models.CharField(
        max_length=20,
        choices=EMAIL_INTERFACE_CHOICES,
        default='basic'
    )
