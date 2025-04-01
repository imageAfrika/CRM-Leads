from django.urls import path
from django.contrib.auth.decorators import login_required

from .views import (
    # Email Views
    EmailListView,
    EmailComposeView,
    EmailDetailView,
    EmailSentView,
    EmailDraftView,
    EmailDeleteView,
    
    # Contact Views
    ContactListView,
    ContactCreateView,
    ContactUpdateView,
    ContactDeleteView,
    
    # Calendar Views
    CalendarView,
    EventCreateView,
    EventDetailView,
    EventUpdateView,
    EventDeleteView,
    EventListView,
    
    # Messaging Views
    MessageInboxView,
    WhatsAppMessageView,
    TelegramMessageView,
    MessageComposeView,
    
    # Notification Views
    NotificationListView,
    NotificationMarkReadView,
    NotificationCreateView,
    NotificationDetailView,
    NotificationUpdateView,
    NotificationDeleteView,
    NotificationMarkAllReadView,
)

from . import views_telebird

app_name = 'communication'

urlpatterns = [
    # Telebird Communication URLs
    path('telebird/', views_telebird.TelebirdIntroView.as_view(), name='telebird_intro'),
    path('telebird/email/', login_required(views_telebird.TelebirdEmailInboxView.as_view()), name='telebird_email_inbox'),
    path('telebird/telegram/', login_required(views_telebird.TelebirdTelegramClientView.as_view()), name='telebird_telegram_client'),
    
    # Email Settings URL
    path('email/settings/', login_required(views_telebird.EmailSettingsView.as_view()), name='email_settings'),

    # Email URLs
    path('email/', login_required(EmailListView.as_view()), name='email_inbox'),
    path('email/compose/', login_required(EmailComposeView.as_view()), name='email_compose'),
    path('email/sent/', login_required(EmailSentView.as_view()), name='email_sent'),
    path('email/drafts/', login_required(EmailDraftView.as_view()), name='email_drafts'),
    path('email/<uuid:pk>/', login_required(EmailDetailView.as_view()), name='email_detail'),
    path('email/delete/<uuid:pk>/', login_required(EmailDeleteView.as_view()), name='email_delete'),

    # Telebird email interface URLs
    path('telebird/inbox/', login_required(views_telebird.TelebirdEmailInboxView.as_view()), name='email_inbox_telebird'),
    path('telebird/sent/', login_required(views_telebird.TelebirdEmailSentView.as_view()), name='email_sent_telebird'),
    path('telebird/drafts/', login_required(views_telebird.TelebirdEmailDraftsView.as_view()), name='email_drafts_telebird'),
    path('telebird/compose/', login_required(views_telebird.TelebirdEmailComposeView.as_view()), name='email_compose_telebird'),
    path('telebird/<int:pk>/', login_required(views_telebird.TelebirdEmailViewView.as_view()), name='email_view_telebird'),
    path('telebird/<int:pk>/delete/', login_required(views_telebird.TelebirdEmailDeleteView.as_view()), name='email_delete_telebird'),

    # Contact URLs
    path('contacts/', login_required(ContactListView.as_view()), name='contact_list'),
    path('contacts/add/', login_required(ContactCreateView.as_view()), name='contact_add'),
    path('contacts/edit/<uuid:pk>/', login_required(ContactUpdateView.as_view()), name='contact_edit'),
    path('contacts/delete/<uuid:pk>/', login_required(ContactDeleteView.as_view()), name='contact_delete'),

    # Calendar and Event URLs
    path('calendar/', login_required(CalendarView.as_view()), name='calendar'),
    path('events/', login_required(EventListView.as_view()), name='event_list'),
    path('events/create/', login_required(EventCreateView.as_view()), name='event_create'),
    path('events/<uuid:pk>/', login_required(EventDetailView.as_view()), name='event_detail'),
    path('events/<uuid:pk>/edit/', login_required(EventUpdateView.as_view()), name='event_update'),
    path('events/<uuid:pk>/delete/', login_required(EventDeleteView.as_view()), name='event_delete'),

    # Messaging URLs
    path('messaging/', login_required(MessageInboxView.as_view()), name='messaging_inbox'),
    path('messaging/whatsapp/', WhatsAppMessageView.as_view(), name='whatsapp_messages'),
    path('messaging/telegram/', TelegramMessageView.as_view(), name='telegram_messages'),
    path('messaging/compose/', login_required(MessageComposeView.as_view()), name='message_compose'),

    # Notifications
    path('notifications/', login_required(NotificationListView.as_view()), name='notification_list'),
    path('notifications/create/', login_required(NotificationCreateView.as_view()), name='notification_create'),
    path('notifications/<uuid:pk>/', login_required(NotificationDetailView.as_view()), name='notification_detail'),
    path('notifications/edit/<uuid:pk>/', login_required(NotificationUpdateView.as_view()), name='notification_edit'),
    path('notifications/delete/<uuid:pk>/', login_required(NotificationDeleteView.as_view()), name='notification_delete'),
    path('notifications/mark-read/<uuid:pk>/', login_required(NotificationMarkReadView.as_view()), name='notification_mark_read'),
    path('notifications/mark-all-read/', login_required(NotificationMarkAllReadView.as_view()), name='notification_mark_all_read'),
]

# Optional: API-related URL patterns can be added here in the future
# For example:
# path('api/email/', EmailAPIView.as_view(), name='email_api'),
# path('api/contacts/', ContactAPIView.as_view(), name='contacts_api'),
