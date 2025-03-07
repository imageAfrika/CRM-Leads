from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Product URLs
    path('', views.product_list, name='product_list'),
    path('create/', views.product_create, name='product_create'),
    path('<int:pk>/', views.product_detail, name='product_detail'),
    path('<int:pk>/update/', views.product_update, name='product_update'),
    path('<int:pk>/delete/', views.product_delete, name='product_delete'),
    
    # Category URLs
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/update/', views.category_update, name='category_update'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    
    # Inventory Transaction URLs
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('transactions/create/', views.transaction_create, name='transaction_create'),
    
    # Supplier URLs
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/create/', views.supplier_create, name='supplier_create'),
    path('suppliers/<int:pk>/', views.supplier_detail, name='supplier_detail'),
    path('suppliers/<int:pk>/update/', views.supplier_update, name='supplier_update'),
    path('suppliers/<int:pk>/delete/', views.supplier_delete, name='supplier_delete'),
    
    # Purchase URLs
    path('purchases/', views.purchase_list, name='purchase_list'),
    path('purchases/create/', views.purchase_create, name='purchase_create'),
    path('purchases/<int:pk>/', views.purchase_detail, name='purchase_detail'),
    path('purchases/<int:pk>/update/', views.purchase_update, name='purchase_update'),
    path('purchases/<int:pk>/delete/', views.purchase_delete, name='purchase_delete'),
    
    # Reports
    path('reports/inventory/', views.inventory_report, name='inventory_report'),
    path('reports/sales/', views.sales_report, name='sales_report'),
    path('reports/purchases/', views.purchases_report, name='purchases_report'),
] 