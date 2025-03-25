from django.urls import path
from . import views

app_name = 'leads'

urlpatterns = [
    # Lead URLs
    path('', views.LeadListView.as_view(), name='lead_list'),
    path('create/', views.LeadCreateView.as_view(), name='lead_create'),
    path('<int:pk>/', views.LeadDetailView.as_view(), name='lead_detail'),
    path('<int:pk>/custom/', views.lead_detail_custom, name='lead_detail_custom'),
    path('<int:pk>/update/', views.LeadUpdateView.as_view(), name='lead_update'),
    path('<int:pk>/delete/', views.LeadDeleteView.as_view(), name='lead_delete'),
    path('<int:pk>/convert/', views.LeadConvertView.as_view(), name='lead_convert'),
    
    # Dashboard URL
    path('dashboard/', views.LeadDashboardView.as_view(), name='lead_dashboard'),
    
    # Activity URLs
    path('activity/toggle/', views.activity_toggle, name='activity_toggle'),
    
    # Note URLs
    path('<int:lead_pk>/notes/', views.LeadNoteListView.as_view(), name='lead_note_list'),
    path('<int:lead_pk>/notes/create/', views.LeadNoteCreateView.as_view(), name='lead_note_create'),
    path('<int:lead_pk>/notes/<int:pk>/', views.LeadNoteDetailView.as_view(), name='lead_note_detail'),
    path('<int:lead_pk>/notes/<int:pk>/update/', views.LeadNoteUpdateView.as_view(), name='lead_note_update'),
    path('<int:lead_pk>/notes/<int:pk>/delete/', views.LeadNoteDeleteView.as_view(), name='lead_note_delete'),
    
    # Document URLs
    path('<int:lead_pk>/documents/', views.LeadDocumentListView.as_view(), name='lead_document_list'),
    path('<int:lead_pk>/documents/create/', views.LeadDocumentCreateView.as_view(), name='lead_document_create'),
    path('<int:lead_pk>/documents/<int:pk>/', views.LeadDocumentDetailView.as_view(), name='lead_document_detail'),
    path('<int:lead_pk>/documents/<int:pk>/update/', views.LeadDocumentUpdateView.as_view(), name='lead_document_update'),
    path('<int:lead_pk>/documents/<int:pk>/delete/', views.LeadDocumentDeleteView.as_view(), name='lead_document_delete'),
    
    # Note and document management
    path('leads/<int:pk>/add-note/', views.add_note, name='add_note'),
    path('leads/<int:pk>/add-document/', views.add_document, name='add_document'),
    path('notes/<int:pk>/delete/', views.delete_note, name='delete_note'),
    path('documents/<int:pk>/delete/', views.delete_document, name='delete_document'),
]