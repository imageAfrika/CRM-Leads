from django.urls import path
from . import views

app_name = 'site_admin'

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    
    # Model CRUD operations
    path('<str:app_label>/<str:model_name>/', views.model_list, name='model_list'),
    path('<str:app_label>/<str:model_name>/add/', views.model_add, name='model_add'),
    path('<str:app_label>/<str:model_name>/<int:object_id>/change/', views.model_change, name='model_change'),
    path('<str:app_label>/<str:model_name>/<int:object_id>/delete/', views.model_delete, name='model_delete'),
    
    # User and group management shortcuts
    path('users/', views.user_management, name='user_management'),
    path('groups/', views.group_management, name='group_management'),
    
    # Testing
    path('dark-mode-test/', views.dark_mode_test, name='dark_mode_test'),
]
