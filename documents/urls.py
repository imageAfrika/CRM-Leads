from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    path('', views.DocumentListView.as_view(), name='document_list'),
    path('<int:pk>/', views.DocumentDetailView.as_view(), name='document_detail'),
    path('quote/new/', views.QuoteCreateView.as_view(), name='quote_create'),
    path('quote/<int:pk>/', views.quote_detail, name='quote_detail'),
    path('quote/create/', views.quote_create, name='quote_create_function'),
    path('quote/<int:quote_id>/generate-pdf/', views.generate_quote_pdf, name='generate_quote_pdf'),
] 
