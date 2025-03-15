from django.urls import path
from . import views

app_name = 'leads'

urlpatterns = [
    # Lead URLs
    path('', views.LeadListView.as_view(), name='lead_list'),
    path('create/', views.LeadCreateView.as_view(), name='lead_create'),
    path('<int:pk>/', views.LeadDetailView.as_view(), name='lead_detail'),
    path('<int:pk>/update/', views.LeadUpdateView.as_view(), name='lead_update'),
    path('<int:pk>/delete/', views.LeadDeleteView.as_view(), name='lead_delete'),
    path('<int:pk>/convert/', views.LeadConvertView.as_view(), name='lead_convert'),
    
    # Dashboard URL
    path('dashboard/', views.LeadDashboardView.as_view(), name='lead_dashboard'),
    
    # Activity URLs
    path('activity/toggle/', views.activity_toggle, name='activity_toggle'),
] 