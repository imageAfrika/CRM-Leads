from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse

from .models import Email
from .forms import EmailForm, EmailSettingsForm

class TelebirdIntroView(View):
    def get(self, request):
        return render(request, 'communication/email/telebird_intro.html')

class TelebirdEmailInboxView(LoginRequiredMixin, View):
    def get(self, request):
        # Get inbox emails for the current user
        emails = Email.objects.filter(
            recipients=request.user, 
            is_deleted=False
        ).order_by('-sent_at')
        
        # Get the unread count
        unread_count = emails.filter(is_read=False).count()
        
        # Get the first email to display if available
        current_email = None
        if emails.exists():
            current_email = emails.first()
            # Mark as read
            if not current_email.is_read:
                current_email.is_read = True
                current_email.save()
        
        context = {
            'active_tab': 'inbox',
            'emails': emails,
            'current_email': current_email,
            'unread_count': unread_count
        }
        
        return render(request, 'communication/email/inbox_telebird.html', context)

class TelebirdEmailSentView(LoginRequiredMixin, View):
    def get(self, request):
        # Get sent emails for the current user
        emails = Email.objects.filter(
            sender=request.user, 
            is_deleted=False, 
            is_draft=False
        ).order_by('-sent_at')
        
        # Get the unread count for the inbox
        inbox_emails = Email.objects.filter(recipients=request.user)
        unread_count = inbox_emails.filter(is_read=False).count()
        
        # Get the first email to display if available
        current_email = None
        if emails.exists():
            current_email = emails.first()
        
        context = {
            'active_tab': 'sent',
            'emails': emails,
            'current_email': current_email,
            'unread_count': unread_count
        }
        
        return render(request, 'communication/email/sent_telebird.html', context)

class TelebirdEmailDraftsView(LoginRequiredMixin, View):
    def get(self, request):
        # Get draft emails for the current user
        emails = Email.objects.filter(
            sender=request.user, 
            is_draft=True, 
            is_deleted=False
        ).order_by('-updated_at')
        
        # Get the unread count for the inbox
        inbox_emails = Email.objects.filter(recipients=request.user)
        unread_count = inbox_emails.filter(is_read=False).count()
        
        # Get the first email to display if available
        current_email = None
        if emails.exists():
            current_email = emails.first()
        
        context = {
            'active_tab': 'drafts',
            'emails': emails,
            'current_email': current_email,
            'unread_count': unread_count
        }
        
        return render(request, 'communication/email/inbox_telebird.html', context)

class TelebirdEmailViewView(LoginRequiredMixin, View):
    def get(self, request, pk):
        # Get the email to view
        email = get_object_or_404(Email, pk=pk)
        
        # Mark as read if it's a received email
        if not email.is_read and request.user in email.recipients.all():
            email.is_read = True
            email.save()
        
        # Get all emails based on the current tab
        if email.sender == request.user and email.is_draft:
            active_tab = 'drafts'
            emails = Email.objects.filter(
                sender=request.user, 
                is_draft=True, 
                is_deleted=False
            ).order_by('-updated_at')
        elif email.sender == request.user:
            active_tab = 'sent'
            emails = Email.objects.filter(
                sender=request.user, 
                is_deleted=False, 
                is_draft=False
            ).order_by('-sent_at')
        else:
            active_tab = 'inbox'
            emails = Email.objects.filter(
                recipients=request.user, 
                is_deleted=False
            ).order_by('-sent_at')
        
        # Get the unread count for the inbox
        inbox_emails = Email.objects.filter(recipients=request.user)
        unread_count = inbox_emails.filter(is_read=False).count()
        
        context = {
            'active_tab': active_tab,
            'emails': emails,
            'current_email': email,
            'unread_count': unread_count
        }
        
        return render(request, 'communication/email/view_telebird.html', context)

class TelebirdEmailComposeView(LoginRequiredMixin, View):
    def get(self, request):
        # Initialize form
        form = EmailForm()
        
        # Get the unread count for the inbox
        inbox_emails = Email.objects.filter(recipients=request.user)
        unread_count = inbox_emails.filter(is_read=False).count()
        
        context = {
            'active_tab': 'compose',
            'form': form,
            'unread_count': unread_count
        }
        
        return render(request, 'communication/email/compose_telebird.html', context)
    
    def post(self, request):
        form = EmailForm(request.POST)
        
        if form.is_valid():
            email = form.save(commit=False)
            email.sender_email = request.user.email
            email.sender_name = request.user.get_full_name() or request.user.username
            
            # Check if saving as draft or sending
            if 'save_draft' in request.POST:
                email.is_draft = True
                email.save()
                
                # Save recipients directly to the many-to-many field
                email.recipients.set(form.cleaned_data['recipients'])
                
                messages.success(request, 'Email saved as draft.')
                return redirect('communication:email_drafts_telebird')
            else:
                # Sending the email
                email.is_draft = False
                email.save()
                
                # Save recipients directly to the many-to-many field
                email.recipients.set(form.cleaned_data['recipients'])
                
                # Here you would actually send the email using your email backend
                
                messages.success(request, 'Email sent successfully.')
                return redirect('communication:email_sent_telebird')
        
        # Form is invalid
        context = {
            'active_tab': 'compose',
            'form': form,
            'unread_count': Email.objects.filter(recipients=request.user, is_read=False).count()
        }
        
        return render(request, 'communication/email/compose_telebird.html', context)

class TelebirdEmailDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        email = get_object_or_404(Email, pk=pk)
        
        # Simple soft delete by marking as deleted
        email.is_deleted = True
        email.save()
        
        messages.success(request, 'Email moved to trash.')
        
        # Redirect based on the source
        redirect_to = request.POST.get('redirect_to', 'inbox')
        if redirect_to == 'sent':
            return redirect('communication:email_sent_telebird')
        elif redirect_to == 'drafts':
            return redirect('communication:email_drafts_telebird')
        else:
            return redirect('communication:email_inbox_telebird')

class TelebirdTelegramClientView(LoginRequiredMixin, View):
    def get(self, request):
        # Placeholder for Telegram client view
        # In a real implementation, you'd fetch Telegram messages, contacts, etc.
        context = {
            'active_tab': 'telegram',
            'messages': [],  # Fetch Telegram messages
            'contacts': [],  # Fetch Telegram contacts
        }
        
        return render(request, 'communication/telegram/telegram_client.html', context)

class EmailSettingsView(LoginRequiredMixin, View):
    def get(self, request):
        # Initial email settings form
        initial_data = {
            'display_name': request.user.profile.display_name,
            'signature': request.user.profile.email_signature,
            'theme': request.user.profile.email_theme,
            'language': request.user.profile.language,
        }
        form = EmailSettingsForm(initial=initial_data)
        
        context = {
            'form': form,
            'active_tab': 'settings',
        }
        
        return render(request, 'communication/email/email_settings.html', context)
    
    def post(self, request):
        form = EmailSettingsForm(request.POST)
        
        if form.is_valid():
            # Update user profile with email settings
            profile = request.user.profile
            profile.display_name = form.cleaned_data['display_name']
            profile.email_signature = form.cleaned_data['signature']
            profile.email_theme = form.cleaned_data['theme']
            profile.language = form.cleaned_data['language']
            profile.save()
            
            # AJAX response for dynamic update
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': 'Email settings updated successfully.',
                })
            
            # Traditional form submission
            messages.success(request, 'Email settings updated successfully.')
            return redirect('communication:email_settings')
        
        # If form is invalid
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error',
                'errors': form.errors,
            }, status=400)
        
        # Traditional form submission
        context = {
            'form': form,
            'active_tab': 'settings',
        }
        return render(request, 'communication/email/email_settings.html', context)
