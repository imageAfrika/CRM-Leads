from django.shortcuts import redirect
from django.urls import resolve, reverse
from django.contrib import messages
from django.conf import settings

from .models import UserAppPermission, GroupAppPermission

class AccessControlMiddleware:
    """
    Middleware to check if a user has permission to access a specific view
    """
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Define paths that should be excluded from permission checks
        self.excluded_paths = [
            '/admin/',
            '/auth/',
            '/access-control/',
            '/static/',
            '/media/',
        ]
        
        # Define paths that are always allowed for authenticated users
        self.always_allowed = [
            '/',
            '/dashboard/',
            '/profile/',
        ]
    
    def __call__(self, request):
        # Skip middleware for unauthenticated users
        if not request.user.is_authenticated:
            return self.get_response(request)
        
        # Skip middleware for superusers
        if request.user.is_superuser:
            return self.get_response(request)
        
        # Skip middleware for excluded paths
        path = request.path_info
        if any(path.startswith(excluded) for excluded in self.excluded_paths):
            return self.get_response(request)
        
        # Allow access to always allowed paths
        if any(path == allowed for allowed in self.always_allowed):
            return self.get_response(request)
        
        # Get the app name from the URL
        resolved = resolve(path)
        app_name = resolved.app_name
        
        # If no app name, allow access (likely a root URL)
        if not app_name:
            return self.get_response(request)
        
        # Get the view name
        view_name = resolved.url_name
        
        # Determine permission type based on view name
        permission_type = 'view'  # Default permission type
        if 'create' in view_name or 'add' in view_name:
            permission_type = 'add'
        elif 'update' in view_name or 'edit' in view_name or 'change' in view_name:
            permission_type = 'change'
        elif 'delete' in view_name or 'remove' in view_name:
            permission_type = 'delete'
        
        # Check if user has direct permission
        user_has_permission = UserAppPermission.objects.filter(
            user=request.user,
            permission__app_name=app_name,
            permission__permission_type__in=[permission_type, 'full'],
            permission__is_active=True
        ).exists()
        
        if user_has_permission:
            return self.get_response(request)
        
        # Check if user has permission through a group
        user_groups = request.user.groups.all()
        group_has_permission = GroupAppPermission.objects.filter(
            group__in=user_groups,
            permission__app_name=app_name,
            permission__permission_type__in=[permission_type, 'full'],
            permission__is_active=True
        ).exists()
        
        if group_has_permission:
            return self.get_response(request)
        
        # If user doesn't have permission, redirect to dashboard with error message
        messages.error(request, f"You don't have permission to access this page.")
        return redirect('dashboard')  # Redirect to main dashboard 