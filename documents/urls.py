from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    path('', views.DocumentListView.as_view(), name='document_list'),
    path('<int:pk>/', views.DocumentDetailView.as_view(), name='document_detail'),
    path('<int:pk>/edit/', views.DocumentUpdateView.as_view(), name='document_edit'),
    path('<int:pk>/download/', views.document_download, name='document_download'),
    path('quote/new/', views.QuoteCreateView.as_view(), name='quote_create'),
    path('quote/create/', views.quote_create, name='quote_create_function'),
    path('quote/<int:pk>/', views.quote_detail, name='quote_detail'),
    path('quote/<int:quote_id>/generate-pdf/', views.generate_quote_pdf, name='generate_quote_pdf'),
    path('quote/get-number/', views.get_quote_number, name='get_quote_number'),
    path('quote/<int:quote_id>/generate-invoice/', views.generate_invoice_from_quote, name='generate_invoice_from_quote'),
    path('expenditure/', views.expenditure_view, name='expenditure'),
    path('expenditure/create/', views.expenditure_create, name='expenditure_create'),
    path('expenditure/<int:pk>/edit/', views.expenditure_edit, name='expenditure_edit'),
    path('expenditure/<int:pk>/delete/', views.expenditure_delete, name='expenditure_delete'),
    path('invoices/', views.invoice_list, name='invoice_list'),
] 
