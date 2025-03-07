from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import resolve

from .models import UserAppPermission, GroupAppPermission

def permission_required(app_name, permission_type='view', feature=None):
    """
    Decorator to check if a user has permission to access a view
    
    Args:
        app_name (str): The name of the app
        permission_type (str): The type of permission (view, add, change, delete, full)
        feature (str, optional): The specific feature within the app
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Skip check for superusers
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # Check if user has direct permission
            user_has_permission = UserAppPermission.objects.filter(
                user=request.user,
                permission__app_name=app_name,
                permission__feature=feature,
                permission__permission_type__in=[permission_type, 'full'],
                permission__is_active=True
            ).exists()
            
            if user_has_permission:
                return view_func(request, *args, **kwargs)
            
            # Check if user has permission through a group
            user_groups = request.user.groups.all()
            group_has_permission = GroupAppPermission.objects.filter(
                group__in=user_groups,
                permission__app_name=app_name,
                permission__feature=feature,
                permission__permission_type__in=[permission_type, 'full'],
                permission__is_active=True
            ).exists()
            
            if group_has_permission:
                return view_func(request, *args, **kwargs)
            
            # If user doesn't have permission, redirect to dashboard with error message
            messages.error(request, f"You don't have permission to access this page.")
            return redirect('dashboard')  # Redirect to main dashboard
        
        return _wrapped_view
    
    return decorator

def has_permission(user, app_name, permission_type='view', feature=None):
    """
    Check if a user has permission to access a feature
    
    Args:
        user (User): The user to check
        app_name (str): The name of the app
        permission_type (str): The type of permission (view, add, change, delete, full)
        feature (str, optional): The specific feature within the app
        
    Returns:
        bool: True if the user has permission, False otherwise
    """
    # Skip check for superusers
    if user.is_superuser:
        return True
    
    # Check if user has direct permission
    user_has_permission = UserAppPermission.objects.filter(
        user=user,
        permission__app_name=app_name,
        permission__feature=feature,
        permission__permission_type__in=[permission_type, 'full'],
        permission__is_active=True
    ).exists()
    
    if user_has_permission:
        return True
    
    # Check if user has permission through a group
    user_groups = user.groups.all()
    group_has_permission = GroupAppPermission.objects.filter(
        group__in=user_groups,
        permission__app_name=app_name,
        permission__feature=feature,
        permission__permission_type__in=[permission_type, 'full'],
        permission__is_active=True
    ).exists()
    
    return group_has_permission 