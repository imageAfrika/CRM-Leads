from django import forms
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from .models import (
    Contact, 
    Email, 
    EmailAttachment, 
    Event, 
    WhatsAppMessage, 
    TelegramMessage,
    Notification
)

User = get_user_model()

class MultipleFileInput(forms.ClearableFileInput):
    """
    Custom file input to support multiple file uploads.
    """
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    """
    Custom file field to support multiple file uploads.
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        """
        Validate multiple file uploads.
        """
        if not data and initial:
            return initial

        if not data:
            return None

        files = data if isinstance(data, list) else [data]
        
        # Validate each file
        for file in files:
            super().clean(file)
        
        return files

class ContactForm(forms.ModelForm):
    """
    Form for creating and updating contacts
    """
    class Meta:
        model = Contact
        fields = [
            'first_name', 
            'last_name', 
            'email', 
            'phone_number', 
            'messenger_type', 
            'messenger_id', 
            'company', 
            'notes'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'messenger_type': forms.Select(attrs={'class': 'form-select'}),
            'messenger_id': forms.TextInput(attrs={'class': 'form-control'}),
            'company': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        """
        Set the user for the contact.
        """
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        """
        Associate the contact with the current user.
        """
        contact = super().save(commit=False)
        if self.user:
            contact.user = self.user
        
        if commit:
            contact.save()
        return contact

class EmailComposeForm(forms.ModelForm):
    """
    Form for composing and sending emails with multiple attachments.
    """
    # Define recipients and cc as separate fields since they're ManyToMany
    recipients = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
        required=True,
        help_text='Select one or more recipients'
    )
    
    cc = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
        required=False,
        help_text='Select users to CC (optional)'
    )
    
    attachments = MultipleFileField(
        required=False,
        help_text='Select multiple files to attach (PDF, DOC, DOCX, JPG, PNG, TXT, XLSX)',
        validators=[FileExtensionValidator(['pdf', 'doc', 'docx', 'jpg', 'png', 'txt', 'xlsx'])]
    )

    class Meta:
        model = Email
        fields = ['recipients', 'cc', 'subject', 'body', 'attachments']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': 'Compose your message here...'})
        }
    
    def __init__(self, *args, **kwargs):
        """
        Set up user-specific recipient lists
        """
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Get all users for the same company as the current user
            # This assumes there's a Profile model with a company field
            self.fields['recipients'].queryset = User.objects.exclude(id=user.id)
            self.fields['cc'].queryset = User.objects.exclude(id=user.id)
            
            # If we're editing an existing email
            if self.instance and self.instance.pk:
                # Pre-select recipients and cc
                if hasattr(self.instance, 'recipients'):
                    self.initial['recipients'] = self.instance.recipients.all()
                if hasattr(self.instance, 'cc'):
                    self.initial['cc'] = self.instance.cc.all()

    def clean(self):
        """
        Validate the form data
        """
        cleaned_data = super().clean()
        
        # Ensure at least one recipient is selected
        if not cleaned_data.get('recipients'):
            self.add_error('recipients', 'You must specify at least one recipient')
            
        # Ensure subject is not empty
        if not cleaned_data.get('subject'):
            self.add_error('subject', 'Subject cannot be empty')
            
        return cleaned_data

    def save(self, commit=True):
        """
        Save email and handle multiple attachments.
        """
        email = super().save(commit=False)
        
        if commit:
            email.save()

        # Handle attachments
        if self.cleaned_data.get('attachments'):
            for uploaded_file in self.cleaned_data['attachments']:
                attachment = EmailAttachment.objects.create(file=uploaded_file)
                email.attachments.add(attachment)

        return email

class EventForm(forms.ModelForm):
    """
    Form for creating and editing calendar events with comprehensive functionality.
    """
    # Additional fields for enhanced event creation
    attendee_emails = forms.CharField(
        required=False, 
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter email addresses separated by comma'}),
        help_text='Add additional attendees by email'
    )
    
    # Recurrence fields
    is_recurring = forms.BooleanField(
        required=False, 
        label='Make this a recurring event',
        help_text='Check if this event repeats periodically'
    )
    
    class Meta:
        model = Event
        fields = [
            'title', 'description', 'start_time', 'end_time', 
            'location', 'category', 'privacy', 'color',
            'recurrence_type', 'recurrence_interval', 'recurrence_end_date',
            'send_email_reminder', 'send_sms_reminder', 'send_whatsapp_reminder',
            'video_conference_link', 'external_link'
        ]
        
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'color': forms.TextInput(attrs={'type': 'color'}),
            'recurrence_end_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def clean(self):
        """
        Validate form data with comprehensive checks.
        """
        cleaned_data = super().clean()
        
        # Validate time range
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        if start_time and end_time:
            if start_time >= end_time:
                raise forms.ValidationError("End time must be after start time.")
        
        # Validate recurring event details
        is_recurring = cleaned_data.get('is_recurring')
        recurrence_type = cleaned_data.get('recurrence_type')
        recurrence_interval = cleaned_data.get('recurrence_interval')
        
        if is_recurring:
            if recurrence_type == 'none':
                raise forms.ValidationError("Please select a recurrence type for recurring events.")
            
            if recurrence_interval < 1:
                raise forms.ValidationError("Recurrence interval must be at least 1.")
        
        # Process attendee emails
        attendee_emails = cleaned_data.get('attendee_emails', '').strip()
        if attendee_emails:
            email_list = [email.strip() for email in attendee_emails.split(',')]
            # Validate email format and find corresponding contacts
            valid_contacts = []
            for email in email_list:
                try:
                    contact = Contact.objects.get(email__iexact=email)
                    valid_contacts.append(contact)
                except Contact.DoesNotExist:
                    raise forms.ValidationError(f"No contact found with email: {email}")
            
            cleaned_data['attendees'] = valid_contacts
        
        return cleaned_data
    
    def save(self, user, commit=True):
        """
        Custom save method to associate the event with the current user.
        """
        event = super().save(commit=False)
        event.user = user
        
        if commit:
            event.save()
            
            # Handle many-to-many relationships after saving
            if 'attendees' in self.cleaned_data:
                event.attendees.set(self.cleaned_data['attendees'])
        
        return event

class WhatsAppMessageForm(forms.ModelForm):
    """
    Form for creating WhatsApp messages
    """
    contact = forms.ModelChoiceField(
        queryset=Contact.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Recipient Contact'
    )
    message_text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 4, 
            'placeholder': 'Type your WhatsApp message...'
        }),
        label='Message',
        max_length=1000
    )
    media_file = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
        label='Optional Media File'
    )

    class Meta:
        model = WhatsAppMessage
        fields = ['contact', 'message_text', 'media_file']

    def __init__(self, *args, **kwargs):
        """
        Limit contact queryset to user's contacts
        """
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['contact'].queryset = Contact.objects.filter(user=user)

    def clean_message_text(self):
        """
        Validate message body
        """
        message_text = self.cleaned_data['message_text']
        if len(message_text.strip()) == 0:
            raise forms.ValidationError('Message cannot be empty.')
        return message_text

class TelegramMessageForm(forms.ModelForm):
    """
    Form for creating Telegram messages
    """
    contact = forms.ModelChoiceField(
        queryset=Contact.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Recipient Contact'
    )
    message_text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 4, 
            'placeholder': 'Type your Telegram message...'
        }),
        label='Message',
        max_length=1000
    )
    media_file = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
        label='Optional Media File'
    )

    class Meta:
        model = TelegramMessage
        fields = ['contact', 'message_text', 'media_file']

    def __init__(self, *args, **kwargs):
        """
        Limit contact queryset to user's contacts
        """
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['contact'].queryset = Contact.objects.filter(user=user)

    def clean_message_text(self):
        """
        Validate message body
        """
        message_text = self.cleaned_data['message_text']
        if len(message_text.strip()) == 0:
            raise forms.ValidationError('Message cannot be empty.')
        return message_text

class NotificationForm(forms.ModelForm):
    """
    Form for creating and managing notifications
    """
    class Meta:
        model = Notification
        fields = [
            'title', 
            'message', 
            'notification_type', 
            'is_read', 
            'related_object_id'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'notification_type': forms.Select(attrs={'class': 'form-select'}),
            'is_read': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'related_object_id': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        """
        Set the user for the notification.
        """
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        """
        Associate the notification with the current user.
        """
        notification = super().save(commit=False)
        if self.user:
            notification.user = self.user
        
        if commit:
            notification.save()
        return notification

class EmailForm(forms.ModelForm):
    """Form for composing emails for the Telebird interface"""
    recipients = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2'}),
        help_text="Select one or more recipients"
    )
    
    class Meta:
        model = Email
        fields = ['recipients', 'subject', 'body']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
        }

class EmailSettingsForm(forms.Form):
    """
    Form for managing email client settings
    """
    THEME_CHOICES = [
        ('light', 'Light Theme'),
        ('dark', 'Dark Theme'),
        ('ocean', 'Ocean Blue'),
        ('forest', 'Forest Green'),
    ]

    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('fr', 'French'),
        ('es', 'Spanish'),
        ('de', 'German'),
        ('zh', 'Chinese'),
    ]

    display_name = forms.CharField(
        label='Display Name',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your display name for emails'
        })
    )

    signature = forms.CharField(
        label='Email Signature',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Optional email signature',
            'rows': 3
        })
    )

    theme = forms.ChoiceField(
        label='Email Client Theme',
        choices=THEME_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    language = forms.ChoiceField(
        label='Language',
        choices=LANGUAGE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    def clean_signature(self):
        """
        Validate email signature length
        """
        signature = self.cleaned_data.get('signature', '')
        if len(signature) > 500:
            raise forms.ValidationError('Signature must be 500 characters or less.')
        return signature
