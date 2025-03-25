from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    ListView, 
    CreateView, 
    UpdateView, 
    DeleteView, 
    DetailView, 
    TemplateView,
    FormView,
    View
)
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone

from .models import (
    Contact, 
    Email, 
    Event, 
    Notification, 
    WhatsAppMessage, 
    TelegramMessage,
    EmailAttachment
)
from .forms import (
    ContactForm, 
    EmailComposeForm, 
    EventForm, 
    WhatsAppMessageForm, 
    TelegramMessageForm,
    NotificationForm
)

class EmailListView(LoginRequiredMixin, ListView):
    """
    View for displaying emails in the inbox.
    """
    model = Email
    template_name = 'communication/email/inbox.html'
    context_object_name = 'emails'
    paginate_by = 20

    def get_queryset(self):
        """
        Get emails where the current user is either a recipient, CC'd, or the sender.
        """
        # Get emails where user is recipient, CC'd, or sender
        queryset = Email.objects.filter(
            Q(recipients=self.request.user) | 
            Q(cc=self.request.user) |
            Q(sender=self.request.user)
        ).distinct().order_by('-sent_at')

        # Search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(subject__icontains=search_query) | 
                Q(body__icontains=search_query)
            )

        # Filter by status
        status = self.request.GET.get('status', '')
        if status:
            queryset = queryset.filter(status=status)

        return queryset

    def get_context_data(self, **kwargs):
        """
        Add additional context for filtering and search.
        """
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['status_filter'] = self.request.GET.get('status', '')
        return context


class EmailComposeView(LoginRequiredMixin, FormView):
    """
    View for composing and sending emails.
    """
    template_name = 'communication/email/compose.html'
    form_class = EmailComposeForm
    success_url = reverse_lazy('communication:email_sent')
    
    def get_initial(self):
        """
        Pre-populate form fields for replies or forwards.
        """
        initial = super().get_initial()
        
        # Handle reply to email
        reply_to_id = self.request.GET.get('reply_to')
        if reply_to_id:
            try:
                original_email = Email.objects.get(pk=reply_to_id)
                initial['subject'] = f"Re: {original_email.subject}"
                initial['body'] = f"\n\n----- Original Message -----\nFrom: {original_email.sender.get_full_name() or original_email.sender.username}\nDate: {original_email.sent_at.strftime('%Y-%m-%d %H:%M')}\nSubject: {original_email.subject}\n\n{original_email.body}"
                # Add original sender as recipient
                initial['recipients'] = [original_email.sender.id]
            except Email.DoesNotExist:
                pass
                
        # Handle forward
        forward_id = self.request.GET.get('forward')
        if forward_id:
            try:
                original_email = Email.objects.get(pk=forward_id)
                initial['subject'] = f"Fwd: {original_email.subject}"
                initial['body'] = f"\n\n----- Forwarded Message -----\nFrom: {original_email.sender.get_full_name() or original_email.sender.username}\nDate: {original_email.sent_at.strftime('%Y-%m-%d %H:%M')}\nSubject: {original_email.subject}\n\n{original_email.body}"
                # Attachments will be handled in get_context_data
            except Email.DoesNotExist:
                pass
                
        # Handle draft editing
        draft_id = self.request.GET.get('draft')
        if draft_id:
            try:
                draft = Email.objects.get(pk=draft_id, sender=self.request.user, status='draft')
                initial['subject'] = draft.subject
                initial['body'] = draft.body
                initial['recipients'] = draft.recipients.all().values_list('id', flat=True)
                initial['cc'] = draft.cc.all().values_list('id', flat=True)
                # Attachments will be handled in get_context_data
                self.draft_id = draft_id
            except Email.DoesNotExist:
                self.draft_id = None
        else:
            self.draft_id = None
            
        return initial
    
    def get_context_data(self, **kwargs):
        """
        Add additional context for the template.
        """
        context = super().get_context_data(**kwargs)
        
        # Add draft status
        context['is_draft'] = bool(self.request.GET.get('draft'))
        
        # Handle existing attachments for drafts or forwards
        if hasattr(self, 'draft_id') and self.draft_id:
            draft = Email.objects.get(pk=self.draft_id)
            context['existing_attachments'] = draft.attachments.all()
            
        # For forwarded emails, include original attachments
        forward_id = self.request.GET.get('forward')
        if forward_id:
            try:
                original_email = Email.objects.get(pk=forward_id)
                context['existing_attachments'] = original_email.attachments.all()
            except Email.DoesNotExist:
                pass
                
        return context
    
    def get_form_kwargs(self):
        """
        Pass the current user to the form.
        """
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        """
        Process and send the email.
        """
        # Check if we're updating a draft
        draft_id = self.request.GET.get('draft')
        if draft_id:
            try:
                email = Email.objects.get(pk=draft_id, sender=self.request.user, status='draft')
                # Update existing draft
                email.subject = form.cleaned_data['subject']
                email.body = form.cleaned_data['body']
                
                # Clear existing recipients and CC to add new ones
                email.recipients.clear()
                email.cc.clear()
                
                # Handle attachments - remove unchecked ones
                if self.request.POST:
                    for attachment in email.attachments.all():
                        if f'keep_attachment_{attachment.id}' not in self.request.POST:
                            email.attachments.remove(attachment)
            except Email.DoesNotExist:
                # Create new email if draft not found
                email = form.save(commit=False)
                email.sender = self.request.user
                email.save()
        else:
            # Create new email
            email = form.save(commit=False)
            email.sender = self.request.user
            email.save()
        
        # Add recipients and CC recipients
        for recipient in form.cleaned_data['recipients']:
            email.recipients.add(recipient)
            
        if form.cleaned_data.get('cc'):
            for cc_recipient in form.cleaned_data['cc']:
                email.cc.add(cc_recipient)
        
        # Handle attachments
        if form.cleaned_data.get('attachments'):
            for attachment_file in form.cleaned_data['attachments']:
                attachment = EmailAttachment(file=attachment_file)
                attachment.save()
                email.attachments.add(attachment)
        
        # Check if saving as draft or sending
        if 'save_draft' in self.request.POST:
            email.status = 'draft'
            email.save()
            messages.success(self.request, 'Email saved as draft.')
            return redirect('communication:email_drafts')
        else:
            # Send the email
            email.status = 'sent'
            email.sent_at = timezone.now()
            email.save()
            
            # Create notification for recipients
            for recipient in email.recipients.all():
                Notification.objects.create(
                    user=recipient,
                    title=f"New Email: {email.subject}",
                    message=f"You have received a new email from {email.sender.get_full_name() or email.sender.username}",
                    notification_type='email',
                    related_object_id=email.id
                )
            
            messages.success(self.request, 'Email sent successfully!')
            return redirect('communication:email_sent')

    def form_invalid(self, form):
        """
        Handle form validation errors.
        """
        messages.error(self.request, 'There was an error sending your email. Please check the form.')
        return super().form_invalid(form)


class EmailDetailView(LoginRequiredMixin, DetailView):
    """
    View for displaying a specific email.
    """
    model = Email
    template_name = 'communication/email/view.html'
    context_object_name = 'email'

    def get(self, request, *args, **kwargs):
        """
        Mark email as read when viewed by a recipient.
        """
        email = self.get_object()
        
        # Check if current user is a recipient and email is unread
        if request.user in email.recipients.all() and email.status != 'read':
            email.status = 'read'
            email.save()
            
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        """
        Add additional context for the template.
        """
        context = super().get_context_data(**kwargs)
        # Add flag to indicate if user is sender or recipient
        context['is_sender'] = self.object.sender == self.request.user
        context['is_recipient'] = self.request.user in self.object.recipients.all()
        return context


class EmailSentView(LoginRequiredMixin, ListView):
    """
    View for displaying sent emails.
    """
    model = Email
    template_name = 'communication/email/sent.html'
    context_object_name = 'emails'
    paginate_by = 20

    def get_queryset(self):
        """
        Get emails sent by the current user.
        """
        queryset = Email.objects.filter(
            sender=self.request.user,
            status__in=['sent', 'delivered', 'read']
        ).order_by('-sent_at')
        
        # Search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(subject__icontains=search_query) | 
                Q(body__icontains=search_query)
            )
            
        return queryset
    
    def get_context_data(self, **kwargs):
        """
        Add additional context for the template.
        """
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context


class EmailDraftView(LoginRequiredMixin, ListView):
    """
    View for displaying email drafts.
    """
    model = Email
    template_name = 'communication/email/drafts.html'
    context_object_name = 'emails'
    paginate_by = 20

    def get_queryset(self):
        """
        Get draft emails created by the current user.
        """
        queryset = Email.objects.filter(
            sender=self.request.user,
            status='draft'
        ).order_by('-updated_at')
        
        # Search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(subject__icontains=search_query) | 
                Q(body__icontains=search_query)
            )
            
        return queryset
    
    def get_context_data(self, **kwargs):
        """
        Add additional context for the template.
        """
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context


class EmailDeleteView(LoginRequiredMixin, DeleteView):
    """
    View for deleting an email.
    """
    model = Email
    template_name = 'communication/email/delete.html'
    context_object_name = 'email'
    
    def get_success_url(self):
        """
        Redirect based on the email status and user role.
        """
        # If it was a draft, go to drafts
        if self.object.status == 'draft':
            return reverse_lazy('communication:email_drafts')
        # If user was the sender, go to sent
        elif self.object.sender == self.request.user:
            return reverse_lazy('communication:email_sent')
        # Otherwise go to inbox
        else:
            return reverse_lazy('communication:email_inbox')
    
    def get_queryset(self):
        """
        Ensure users can only delete their own emails or emails they've received.
        """
        return Email.objects.filter(
            Q(sender=self.request.user) | 
            Q(recipients=self.request.user)
        ).distinct()


class ContactListView(LoginRequiredMixin, ListView):
    """
    View for displaying user's contacts with search and filtering.
    """
    model = Contact
    template_name = 'communication/contacts/list.html'
    context_object_name = 'contacts'
    paginate_by = 20

    def get_queryset(self):
        """
        Filter contacts with optional search.
        """
        queryset = Contact.objects.filter(user=self.request.user)
        
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(first_name__icontains=search_query) | 
                Q(last_name__icontains=search_query) | 
                Q(email__icontains=search_query) |
                Q(phone_number__icontains=search_query)
            )
        
        return queryset.order_by('first_name', 'last_name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context


class ContactCreateView(LoginRequiredMixin, CreateView):
    """
    View for creating a new contact.
    """
    model = Contact
    form_class = ContactForm
    template_name = 'communication/contacts/add_edit.html'
    success_url = reverse_lazy('communication:contact_list')

    def form_valid(self, form):
        """
        Set the user for the contact and save.
        """
        form.instance.user = self.request.user
        messages.success(self.request, 'Contact created successfully!')
        return super().form_valid(form)


class ContactUpdateView(LoginRequiredMixin, UpdateView):
    """
    View for updating an existing contact.
    """
    model = Contact
    form_class = ContactForm
    template_name = 'communication/contacts/add_edit.html'
    success_url = reverse_lazy('communication:contact_list')

    def get_queryset(self):
        """
        Ensure user can only update their own contacts.
        """
        return Contact.objects.filter(user=self.request.user)

    def form_valid(self, form):
        """
        Add success message.
        """
        messages.success(self.request, 'Contact updated successfully!')
        return super().form_valid(form)


class ContactDeleteView(LoginRequiredMixin, DeleteView):
    """
    View for deleting a contact.
    """
    model = Contact
    template_name = 'communication/contacts/delete.html'
    success_url = reverse_lazy('communication:contact_list')

    def get_queryset(self):
        """
        Ensure user can only delete their own contacts.
        """
        return Contact.objects.filter(user=self.request.user)


class ContactDetailView(LoginRequiredMixin, DetailView):
    """
    View for displaying contact details.
    """
    model = Contact
    template_name = 'communication/contacts/detail.html'
    context_object_name = 'contact'

    def get_queryset(self):
        """
        Ensure users can only view their own contacts.
        """
        return Contact.objects.filter(user=self.request.user)


class CalendarView(LoginRequiredMixin, TemplateView):
    """
    View for displaying the calendar with events.
    """
    template_name = 'communication/calendar/calendar.html'

    def get_context_data(self, **kwargs):
        """
        Provide events for the current user.
        """
        context = super().get_context_data(**kwargs)
        
        # Get contacts for the current user
        user_contacts = Contact.objects.filter(user=self.request.user)
        
        # Filter events where the user is the owner or an attendee is one of their contacts
        context['events'] = Event.objects.filter(
            Q(user=self.request.user) | 
            Q(attendees__in=user_contacts)
        ).distinct().order_by('start_time')
        
        return context


class EventCreateView(LoginRequiredMixin, CreateView):
    """
    View for creating a new calendar event.
    """
    model = Event
    form_class = EventForm
    template_name = 'communication/calendar/add_edit_event.html'
    success_url = reverse_lazy('communication:calendar')

    def get_form_kwargs(self):
        """
        Pass the current user to the form to filter contacts.
        """
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        """
        Set the event creator and save.
        """
        form.instance.user = self.request.user
        response = super().form_valid(form)
        
        # Create a notification for the event
        Notification.objects.create(
            user=self.request.user,
            title=f"New Event: {form.instance.title}",
            message=f"Event scheduled for {form.instance.start_time.strftime('%Y-%m-%d %H:%M')}",
            notification_type='event_reminder',
            related_object_id=form.instance.id
        )
        
        messages.success(self.request, 'Event created successfully!')
        return response


class EventDetailView(LoginRequiredMixin, DetailView):
    """
    View for displaying a specific event details.
    """
    model = Event
    template_name = 'communication/calendar/event_detail.html'
    context_object_name = 'event'


class EventUpdateView(LoginRequiredMixin, UpdateView):
    """
    View for updating an existing event.
    """
    model = Event
    form_class = EventForm
    template_name = 'communication/calendar/add_edit_event.html'
    success_url = reverse_lazy('communication:calendar')

    def get_form_kwargs(self):
        """
        Pass the current user to the form to filter contacts.
        """
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_queryset(self):
        """
        Ensure user can only update their own events.
        """
        return Event.objects.filter(user=self.request.user)
        
    def form_valid(self, form):
        """
        Update notification when event is updated.
        """
        response = super().form_valid(form)
        
        # Update or create notification for the event
        Notification.objects.update_or_create(
            user=self.request.user,
            notification_type='event_reminder',
            related_object_id=form.instance.id,
            defaults={
                'title': f"Updated Event: {form.instance.title}",
                'message': f"Event updated for {form.instance.start_time.strftime('%Y-%m-%d %H:%M')}",
                'is_read': False
            }
        )
        
        messages.success(self.request, 'Event updated successfully!')
        return response


class EventDeleteView(LoginRequiredMixin, DeleteView):
    """
    View for deleting an event.
    """
    model = Event
    template_name = 'communication/calendar/delete_event.html'
    success_url = reverse_lazy('communication:calendar')

    def get_queryset(self):
        """
        Ensure user can only delete their own events.
        """
        return Event.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        """
        Delete the event and create a notification about the deletion.
        """
        event = self.get_object()
        event_title = event.title
        event_time = event.start_time
        
        # Delete any existing notifications for this event
        Notification.objects.filter(
            user=request.user,
            notification_type='event_reminder',
            related_object_id=event.id
        ).delete()
        
        # Create a new notification about the deletion
        Notification.objects.create(
            user=request.user,
            title="Event Deleted",
            message=f"The event '{event_title}' scheduled for {event_time.strftime('%Y-%m-%d %H:%M')} has been deleted.",
            notification_type='system'
        )
        
        messages.success(request, 'Event deleted successfully.')
        return super().delete(request, *args, **kwargs)


class MessagingView(LoginRequiredMixin, TemplateView):
    """
    View for displaying messaging options.
    """
    template_name = 'communication/messaging/messaging_view.html'


class WhatsAppMessageView(LoginRequiredMixin, ListView):
    """
    View for managing WhatsApp messages
    """
    model = WhatsAppMessage
    template_name = 'communication/messaging/whatsapp_message.html'
    context_object_name = 'whatsapp_messages'
    paginate_by = 20

    def get_queryset(self):
        """
        Filter messages for the current user
        """
        return WhatsAppMessage.objects.filter(user=self.request.user).order_by('-sent_at')

    def get_context_data(self, **kwargs):
        """
        Add form to context for creating new messages
        """
        context = super().get_context_data(**kwargs)
        context['form'] = WhatsAppMessageForm(user=self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        """
        Handle creating a new WhatsApp message
        """
        form = WhatsAppMessageForm(request.POST, user=request.user)
        if form.is_valid():
            message = form.save(commit=False)
            message.user = request.user
            message.sent_at = timezone.now()
            message.status = 'sent'
            message.save()
            messages.success(request, 'WhatsApp message sent successfully.')
            return redirect('communication:whatsapp_messages')
        
        # If form is invalid, render the page with errors
        return self.get(request, *args, **kwargs)


class TelegramMessageView(LoginRequiredMixin, ListView):
    """
    View for managing Telegram messages
    """
    model = TelegramMessage
    template_name = 'communication/messaging/telegram_message.html'
    context_object_name = 'telegram_messages'
    paginate_by = 20

    def get_queryset(self):
        """
        Filter messages for the current user
        """
        return TelegramMessage.objects.filter(user=self.request.user).order_by('-sent_at')

    def get_context_data(self, **kwargs):
        """
        Add form to context for creating new messages
        """
        context = super().get_context_data(**kwargs)
        context['form'] = TelegramMessageForm(user=self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        """
        Handle creating a new Telegram message
        """
        form = TelegramMessageForm(request.POST, user=request.user)
        if form.is_valid():
            message = form.save(commit=False)
            message.user = request.user
            message.sent_at = timezone.now()
            message.status = 'sent'
            message.save()
            messages.success(request, 'Telegram message sent successfully.')
            return redirect('communication:telegram_messages')
        
        # If form is invalid, render the page with errors
        return self.get(request, *args, **kwargs)


class MessageInboxView(LoginRequiredMixin, TemplateView):
    """
    View for displaying messaging inbox with multiple services.
    """
    template_name = 'communication/messages/inbox.html'

    def get_context_data(self, **kwargs):
        """
        Provide messages from different services.
        """
        context = super().get_context_data(**kwargs)
        context['whatsapp_messages'] = WhatsAppMessage.objects.filter(
            Q(user=self.request.user) 
        ).order_by('-sent_at')
        context['telegram_messages'] = TelegramMessage.objects.filter(
            Q(user=self.request.user) 
        ).order_by('-sent_at')
        return context


class WhatsAppMessageListView(LoginRequiredMixin, ListView):
    """
    View for displaying WhatsApp messages.
    """
    model = WhatsAppMessage
    template_name = 'communication/messages/whatsapp.html'
    context_object_name = 'whatsapp_messages'
    paginate_by = 20

    def get_queryset(self):
        """
        Filter WhatsApp messages for the current user.
        """
        return WhatsAppMessage.objects.filter(user=self.request.user).order_by('-sent_at')


class TelegramMessageListView(LoginRequiredMixin, ListView):
    """
    View for displaying Telegram messages.
    """
    model = TelegramMessage
    template_name = 'communication/messages/telegram.html'
    context_object_name = 'telegram_messages'
    paginate_by = 20

    def get_queryset(self):
        """
        Filter Telegram messages for the current user.
        """
        return TelegramMessage.objects.filter(user=self.request.user).order_by('-sent_at')


class MessageComposeView(LoginRequiredMixin, FormView):
    """
    View for composing messages across different services.
    """
    template_name = 'communication/messages/compose.html'
    
    def get_form_class(self):
        """
        Dynamically select form based on message service.
        """
        service = self.request.GET.get('service', 'whatsapp')
        if service == 'whatsapp':
            return WhatsAppMessageForm
        elif service == 'telegram':
            return TelegramMessageForm
        return WhatsAppMessageForm  # Default

    def get_context_data(self, **kwargs):
        """
        Add service to context.
        """
        context = super().get_context_data(**kwargs)
        context['service'] = self.request.GET.get('service', 'whatsapp')
        return context

    def form_valid(self, form):
        """
        Save message with the current user as sender.
        """
        message = form.save(commit=False)
        message.user = self.request.user
        message.save()
        
        messages.success(self.request, f'Message sent via {form.__class__.__name__}!')
        return super().form_valid(form)


class NotificationListView(LoginRequiredMixin, ListView):
    """
    View for displaying user notifications.
    """
    model = Notification
    template_name = 'communication/notifications/list.html'
    context_object_name = 'notifications'
    paginate_by = 20

    def get_queryset(self):
        """
        Filter notifications for the current user.
        """
        return Notification.objects.filter(
            user=self.request.user
        ).order_by('-created_at')


class NotificationMarkReadView(LoginRequiredMixin, View):
    """
    View for marking a specific notification as read.
    """
    def get(self, request, pk):
        """
        Mark a single notification as read.
        """
        notification = get_object_or_404(
            Notification, 
            pk=pk, 
            user=request.user
        )
        notification.is_read = True
        notification.save()
        
        messages.success(request, 'Notification marked as read.')
        return redirect('communication:notifications')


class NotificationMarkAllReadView(LoginRequiredMixin, View):
    """
    View for marking all notifications as read.
    """
    def get(self, request):
        """
        Mark all notifications as read.
        """
        Notification.objects.filter(
            user=request.user, 
            is_read=False
        ).update(is_read=True)
        messages.success(request, 'All notifications marked as read.')
        return redirect('communication:notification_list')


class WhatsAppMessageListView(LoginRequiredMixin, ListView):
    """
    View for displaying WhatsApp messages.
    """
    model = WhatsAppMessage
    template_name = 'communication/messages/whatsapp.html'
    context_object_name = 'whatsapp_messages'
    paginate_by = 20

    def get_queryset(self):
        """
        Filter WhatsApp messages for the current user.
        """
        return WhatsAppMessage.objects.filter(user=self.request.user).order_by('-sent_at')


class TelegramMessageListView(LoginRequiredMixin, ListView):
    """
    View for displaying Telegram messages.
    """
    model = TelegramMessage
    template_name = 'communication/messages/telegram.html'
    context_object_name = 'telegram_messages'
    paginate_by = 20

    def get_queryset(self):
        """
        Filter Telegram messages for the current user.
        """
        return TelegramMessage.objects.filter(user=self.request.user).order_by('-sent_at')


class NotificationCreateView(LoginRequiredMixin, CreateView):
    """
    View for creating a new notification.
    """
    model = Notification
    form_class = NotificationForm
    template_name = 'communication/notifications/add_edit.html'
    success_url = reverse_lazy('communication:notification_list')

    def form_valid(self, form):
        """
        Set the notification user and save.
        """
        form.instance.user = self.request.user
        messages.success(self.request, 'Notification created successfully!')
        return super().form_valid(form)


class NotificationDetailView(LoginRequiredMixin, DetailView):
    """
    View for displaying a specific notification.
    """
    model = Notification
    template_name = 'communication/notifications/detail.html'
    context_object_name = 'notification'

    def get(self, request, *args, **kwargs):
        """
        Mark notification as read when viewed.
        """
        notification = self.get_object()
        if notification.user == request.user and not notification.is_read:
            notification.is_read = True
            notification.save()
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        """
        Ensure user can only view their own notifications.
        """
        return Notification.objects.filter(user=self.request.user)


class NotificationUpdateView(LoginRequiredMixin, UpdateView):
    """
    View for updating an existing notification.
    """
    model = Notification
    form_class = NotificationForm
    template_name = 'communication/notifications/add_edit.html'
    success_url = reverse_lazy('communication:notification_list')

    def get_queryset(self):
        """
        Ensure user can only update their own notifications.
        """
        return Notification.objects.filter(user=self.request.user)

    def form_valid(self, form):
        """
        Add success message.
        """
        messages.success(self.request, 'Notification updated successfully!')
        return super().form_valid(form)


class NotificationDeleteView(LoginRequiredMixin, DeleteView):
    """
    View for deleting a notification.
    """
    model = Notification
    template_name = 'communication/notifications/delete.html'
    success_url = reverse_lazy('communication:notification_list')

    def get_queryset(self):
        """
        Ensure user can only delete their own notifications.
        """
        return Notification.objects.filter(user=self.request.user)


class EventListView(LoginRequiredMixin, ListView):
    """
    View to list all events for the current user with advanced filtering and sorting.
    """
    model = Event
    template_name = 'communication/calendar/event_list.html'
    context_object_name = 'events'
    paginate_by = 10

    def get_queryset(self):
        """
        Filter events for the current user with optional search and filtering.
        """
        queryset = Event.objects.filter(
            Q(user=self.request.user) | 
            Q(invited_users=self.request.user) | 
            Q(attendees__in=self.request.user.contact_set.all())
        ).distinct()

        # Filter by category
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)

        # Filter by date range
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if start_date and end_date:
            queryset = queryset.filter(
                start_time__range=[start_date, end_date]
            )

        # Search by title or description
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | 
                Q(description__icontains=search_query)
            )

        # Sort events
        sort_by = self.request.GET.get('sort', 'start_time')
        return queryset.order_by(sort_by)

    def get_context_data(self, **kwargs):
        """
        Add additional context for filtering and sorting.
        """
        context = super().get_context_data(**kwargs)
        context['categories'] = Event.CATEGORY_CHOICES
        context['privacy_options'] = Event.PRIVACY_CHOICES
        context['status_options'] = Event.STATUS_CHOICES
        return context


class EventCreateView(LoginRequiredMixin, CreateView):
    """
    View for creating new calendar events with comprehensive functionality.
    """
    model = Event
    form_class = EventForm
    template_name = 'communication/calendar/event_form.html'
    success_url = reverse_lazy('communication:event_list')

    def form_valid(self, form):
        """
        Custom form validation and event creation.
        """
        # Set the user for the event
        form.instance.user = self.request.user
        
        # Additional processing for event creation
        response = super().form_valid(form)
        
        # Send notifications or invites if needed
        self.send_event_notifications(form.instance)
        
        return response

    def send_event_notifications(self, event):
        """
        Send notifications to attendees and invited users.
        """
        # Email notifications
        if event.send_email_reminder:
            self.send_email_notifications(event)
        
        # WhatsApp/SMS notifications if enabled
        if event.send_whatsapp_reminder:
            self.send_whatsapp_notifications(event)

    def send_email_notifications(self, event):
        """
        Send email notifications for the event.
        """
        from django.core.mail import send_mail
        
        # Collect all email addresses
        recipient_emails = [
            contact.email for contact in event.attendees.all() 
            if contact.email
        ]
        
        # Customize email content
        subject = f"Event Invitation: {event.title}"
        message = f"""
        You have been invited to an event:
        
        Title: {event.title}
        Date: {event.start_time}
        Location: {event.location or 'Not specified'}
        
        Description: {event.description or 'No description'}
        
        {'Video Conference Link: ' + event.video_conference_link if event.video_conference_link else ''}
        """
        
        # Send emails
        send_mail(
            subject, 
            message, 
            settings.DEFAULT_FROM_EMAIL, 
            recipient_emails
        )

    def send_whatsapp_notifications(self, event):
        """
        Send WhatsApp notifications for the event.
        """
        # Placeholder for WhatsApp notification logic
        # You would integrate with a WhatsApp API here
        pass

class EventDetailView(LoginRequiredMixin, DetailView):
    """
    Detailed view of a specific event.
    """
    model = Event
    template_name = 'communication/calendar/event_detail.html'
    context_object_name = 'event'

    def get_queryset(self):
        """
        Ensure users can only view their own events or events they're invited to.
        """
        return Event.objects.filter(
            Q(user=self.request.user) | 
            Q(invited_users=self.request.user) | 
            Q(attendees__in=self.request.user.contact_set.all())
        ).distinct()

class EventUpdateView(LoginRequiredMixin, UpdateView):
    """
    View for updating existing calendar events.
    """
    model = Event
    form_class = EventForm
    template_name = 'communication/calendar/event_form.html'
    success_url = reverse_lazy('communication:event_list')

    def get_form_kwargs(self):
        """
        Pass the current user to the form.
        """
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        """
        Additional processing for event updates.
        """
        # Send update notifications
        original_event = self.get_object()
        response = super().form_valid(form)
        
        self.send_event_update_notifications(original_event, form.instance)
        
        return response

    def send_event_update_notifications(self, original_event, updated_event):
        """
        Send notifications about event updates.
        """
        # Similar to create notifications, but highlight changes
        pass

class EventDeleteView(LoginRequiredMixin, DeleteView):
    """
    View for deleting calendar events.
    """
    model = Event
    template_name = 'communication/calendar/event_confirm_delete.html'
    success_url = reverse_lazy('communication:event_list')

    def get_queryset(self):
        """
        Ensure users can only delete their own events.
        """
        return Event.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        """
        Send cancellation notifications before deletion.
        """
        event = self.get_object()
        self.send_cancellation_notifications(event)
        return super().delete(request, *args, **kwargs)

    def send_cancellation_notifications(self, event):
        """
        Send notifications to attendees about event cancellation.
        """
        # Implement notification logic similar to creation
        pass
