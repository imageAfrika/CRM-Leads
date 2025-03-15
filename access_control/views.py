from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.urls import get_resolver
from django.contrib import messages
from django.db.models import Count

from .models import View, Permission

def is_admin(user):
    """Check if user is an admin"""
    return user.is_superuser or user.is_staff

@login_required
@user_passes_test(is_admin)
def manage_permissions(request):
    """
    Main view for managing user permissions.
    Displays a list of users and their permissions in an admin-like interface.
    """
    # Get all non-admin users
    users = User.objects.filter(
        is_superuser=False, 
        is_staff=False
    ).annotate(
        permission_count=Count('access_control_permissions')
    ).order_by('username')
    
    # Get all views grouped by app
    views = View.objects.select_related().order_by(
        'app_name', 'view_name'
    ).annotate(
        user_count=Count('user_permissions')
    )
    
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        view_id = request.POST.get('view_id')
        is_active = request.POST.get('is_active') == 'true'
        
        try:
            user = User.objects.get(id=user_id)
            view = View.objects.get(id=view_id)
            
            permission, created = Permission.objects.get_or_create(
                user=user,
                view=view,
                defaults={
                    'granted_by': request.user,
                    'is_active': is_active
                }
            )
            
            if not created:
                permission.is_active = is_active
                permission.save()
            
            action = "granted" if is_active else "revoked"
            messages.success(
                request,
                f'Permission {action} successfully for {user.username} on {view.name}'
            )
            
            return JsonResponse({
                'status': 'success',
                'message': f'Permission {action} successfully'
            })
            
        except (User.DoesNotExist, View.DoesNotExist) as e:
            messages.error(request, str(e))
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    # Get existing permissions for all users
    user_permissions = {
        user.id: {
            perm.view_id: perm.is_active 
            for perm in user.access_control_permissions.all()
        }
        for user in users
    }
    
    # Get app statistics
    app_stats = View.objects.values('app_name').annotate(
        view_count=Count('id'),
        permission_count=Count('user_permissions')
    )
    
    context = {
        'title': 'Manage User Permissions',
        'users': users,
        'views': views,
        'user_permissions': user_permissions,
        'app_stats': app_stats,
        'total_users': users.count(),
        'total_views': views.count(),
        'total_permissions': Permission.objects.filter(is_active=True).count(),
    }
    
    return render(request, 'access_control/manage.html', context)

@login_required
@user_passes_test(is_admin)
def scan_views(request):
    """
    Scan all apps for views and create corresponding permissions.
    """
    resolver = get_resolver()
    created_count = 0
    updated_count = 0
    
    for app in View.get_available_apps():
        app_name = app.name
        
        # Get all URL patterns for this app
        for pattern in resolver.url_patterns:
            if hasattr(pattern, 'callback') and pattern.callback:
                # Get view name and URL pattern
                view_func = pattern.callback
                if hasattr(view_func, 'view_class'):
                    view_func = view_func.view_class
                
                view_name = view_func.__name__
                url_pattern = str(pattern.pattern)
                
                # Create or update view
                view, created = View.objects.get_or_create(
                    app_name=app_name,
                    view_name=view_name,
                    defaults={
                        'name': f"{view_name}",
                        'url_pattern': url_pattern,
                        'description': f"Access to {view_name} in {app_name}"
                    }
                )
                
                if created:
                    created_count += 1
    else:
                    # Update URL pattern if it changed
                    if view.url_pattern != url_pattern:
                        view.url_pattern = url_pattern
                        view.save()
                        updated_count += 1
    
    messages.success(
        request, 
        f'Successfully scanned views. Created: {created_count}, Updated: {updated_count}'
    )
    return redirect('access_control:manage') 