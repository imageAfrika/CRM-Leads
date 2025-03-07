from django.urls import path
from . import views

app_name = 'access_control'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Permissions
    path('permissions/', views.permission_list, name='permission_list'),
    path('permissions/create/', views.permission_create, name='permission_create'),
    path('permissions/<int:pk>/update/', views.permission_update, name='permission_update'),
    path('permissions/<int:pk>/delete/', views.permission_delete, name='permission_delete'),
    
    # User Permissions
    path('user-permissions/', views.user_permission_list, name='user_permission_list'),
    path('user-permissions/create/', views.user_permission_create, name='user_permission_create'),
    path('user-permissions/<int:pk>/revoke/', views.user_permission_revoke, name='user_permission_revoke'),
    path('users/<int:user_id>/permissions/', views.user_permissions_manage, name='user_permissions_manage'),
    
    # Group Permissions
    path('group-permissions/', views.group_permission_list, name='group_permission_list'),
    path('group-permissions/create/', views.group_permission_create, name='group_permission_create'),
    path('group-permissions/<int:pk>/revoke/', views.group_permission_revoke, name='group_permission_revoke'),
    path('groups/<int:group_id>/permissions/', views.group_permissions_manage, name='group_permissions_manage'),
    
    # Bulk Operations
    path('bulk-grant/', views.bulk_permission_grant, name='bulk_permission_grant'),
    
    # Logs
    path('logs/', views.access_log_list, name='access_log_list'),
    
    # Settings
    path('settings/', views.settings, name='settings'),
    
    # API
    path('api/check-permission/', views.check_permission, name='check_permission'),
] 