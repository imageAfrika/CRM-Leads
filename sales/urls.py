from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    path('', views.SaleListView.as_view(), name='sale_list'),
    path('<int:pk>/', views.SaleDetailView.as_view(), name='sale_detail'),
    path('new/', views.SaleCreateView.as_view(), name='sale_create'),
    path('<int:pk>/edit/', views.SaleUpdateView.as_view(), name='sale_update'),
    path('<int:pk>/delete/', views.SaleDeleteView.as_view(), name='sale_delete'),
]