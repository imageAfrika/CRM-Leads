from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.db import transaction
from django.urls import reverse
from django.http import JsonResponse
from django.core.paginator import Paginator

from .models import AppPermission, UserAppPermission, GroupAppPermission, AccessLog
from .forms import (
    AppPermissionForm, 
    UserAppPermissionForm, 
    GroupAppPermissionForm,
    BulkPermissionForm,
    PermissionRevokeForm
)

# Helper function to check if user is an admin
def is_admin(user):
    return user.is_superuser or user.is_staff

@login_required
@user_passes_test(is_admin)
def dashboard(request):
    """Main dashboard for the access control app"""
    user_count = User.objects.count()
    group_count = Group.objects.count()
    permission_count = AppPermission.objects.count()
    user_permission_count = UserAppPermission.objects.count()
    group_permission_count = GroupAppPermission.objects.count()
    recent_logs = AccessLog.objects.all()[:10]
    
    context = {
        'user_count': user_count,
        'group_count': group_count,
        'permission_count': permission_count,
        'user_permission_count': user_permission_count,
        'group_permission_count': group_permission_count,
        'recent_logs': recent_logs,
    }
    return render(request, 'access_control/dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def permission_list(request):
    """List all app permissions"""
    permissions = AppPermission.objects.all()
    
    # Filter by app name if provided
    app_name = request.GET.get('app')
    if app_name:
        permissions = permissions.filter(app_name=app_name)
    
    # Filter by permission type if provided
    perm_type = request.GET.get('type')
    if perm_type:
        permissions = permissions.filter(permission_type=perm_type)
    
    # Filter by active status if provided
    active = request.GET.get('active')
    if active is not None:
        is_active = active.lower() == 'true'
        permissions = permissions.filter(is_active=is_active)
    
    # Pagination
    paginator = Paginator(permissions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get available apps for filter
    available_apps = AppPermission.get_available_apps()
    app_choices = [(app.name, app.verbose_name) for app in available_apps]
    
    context = {
        'page_obj': page_obj,
        'app_choices': app_choices,
        'permission_types': AppPermission.PERMISSION_TYPES,
        'selected_app': app_name,
        'selected_type': perm_type,
        'selected_active': active,
    }
    return render(request, 'access_control/permission_list.html', context)

@login_required
@user_passes_test(is_admin)
def permission_create(request):
    """Create a new app permission"""
    if request.method == 'POST':
        form = AppPermissionForm(request.POST)
        if form.is_valid():
            permission = form.save()
            messages.success(request, f'Permission "{permission.name}" created successfully.')
            return redirect('access_control:permission_list')
    else:
        form = AppPermissionForm()
    
    context = {
        'form': form,
        'title': 'Create Permission',
    }
    return render(request, 'access_control/permission_form.html', context)

@login_required
@user_passes_test(is_admin)
def permission_update(request, pk):
    """Update an existing app permission"""
    permission = get_object_or_404(AppPermission, pk=pk)
    
    if request.method == 'POST':
        form = AppPermissionForm(request.POST, instance=permission)
        if form.is_valid():
            permission = form.save()
            messages.success(request, f'Permission "{permission.name}" updated successfully.')
            return redirect('access_control:permission_list')
    else:
        form = AppPermissionForm(instance=permission)
    
    context = {
        'form': form,
        'permission': permission,
        'title': 'Update Permission',
    }
    return render(request, 'access_control/permission_form.html', context)

@login_required
@user_passes_test(is_admin)
def permission_delete(request, pk):
    """Delete an app permission"""
    permission = get_object_or_404(AppPermission, pk=pk)
    
    if request.method == 'POST':
        name = permission.name
        permission.delete()
        messages.success(request, f'Permission "{name}" deleted successfully.')
        return redirect('access_control:permission_list')
    
    context = {
        'permission': permission,
    }
    return render(request, 'access_control/permission_confirm_delete.html', context)

@login_required
@user_passes_test(is_admin)
def user_permission_list(request):
    """List all user permissions"""
    user_permissions = UserAppPermission.objects.all()
    
    # Filter by user if provided
    user_id = request.GET.get('user')
    if user_id:
        user_permissions = user_permissions.filter(user_id=user_id)
    
    # Filter by app name if provided
    app_name = request.GET.get('app')
    if app_name:
        user_permissions = user_permissions.filter(permission__app_name=app_name)
    
    # Pagination
    paginator = Paginator(user_permissions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get users and apps for filters
    users = User.objects.all()
    available_apps = AppPermission.get_available_apps()
    app_choices = [(app.name, app.verbose_name) for app in available_apps]
    
    context = {
        'page_obj': page_obj,
        'users': users,
        'app_choices': app_choices,
        'selected_user': user_id,
        'selected_app': app_name,
    }
    return render(request, 'access_control/user_permission_list.html', context)

@login_required
@user_passes_test(is_admin)
def user_permission_create(request):
    """Grant a permission to a user"""
    if request.method == 'POST':
        form = UserAppPermissionForm(request.POST, current_user=request.user)
        if form.is_valid():
            user_permission = form.save()
            
            # Log the action
            AccessLog.objects.create(
                user=request.user,
                target_user=user_permission.user,
                permission=user_permission.permission,
                action='grant',
                notes=f"Granted {user_permission.permission} to {user_permission.user.username}"
            )
            
            messages.success(request, f'Permission granted to {user_permission.user.username} successfully.')
            return redirect('access_control:user_permission_list')
    else:
        form = UserAppPermissionForm(current_user=request.user)
    
    context = {
        'form': form,
        'title': 'Grant Permission to User',
    }
    return render(request, 'access_control/user_permission_form.html', context)

@login_required
@user_passes_test(is_admin)
def user_permission_revoke(request, pk):
    """Revoke a permission from a user"""
    user_permission = get_object_or_404(UserAppPermission, pk=pk)
    
    if request.method == 'POST':
        username = user_permission.user.username
        permission_name = user_permission.permission.name
        
        # Log the action before deleting
        AccessLog.objects.create(
            user=request.user,
            target_user=user_permission.user,
            permission=user_permission.permission,
            action='revoke',
            notes=f"Revoked {permission_name} from {username}"
        )
        
        user_permission.delete()
        messages.success(request, f'Permission revoked from {username} successfully.')
        return redirect('access_control:user_permission_list')
    
    context = {
        'user_permission': user_permission,
    }
    return render(request, 'access_control/user_permission_confirm_revoke.html', context)

@login_required
@user_passes_test(is_admin)
def group_permission_list(request):
    """List all group permissions"""
    group_permissions = GroupAppPermission.objects.all()
    
    # Filter by group if provided
    group_id = request.GET.get('group')
    if group_id:
        group_permissions = group_permissions.filter(group_id=group_id)
    
    # Filter by app name if provided
    app_name = request.GET.get('app')
    if app_name:
        group_permissions = group_permissions.filter(permission__app_name=app_name)
    
    # Pagination
    paginator = Paginator(group_permissions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get groups and apps for filters
    groups = Group.objects.all()
    available_apps = AppPermission.get_available_apps()
    app_choices = [(app.name, app.verbose_name) for app in available_apps]
    
    context = {
        'page_obj': page_obj,
        'groups': groups,
        'app_choices': app_choices,
        'selected_group': group_id,
        'selected_app': app_name,
    }
    return render(request, 'access_control/group_permission_list.html', context)

@login_required
@user_passes_test(is_admin)
def group_permission_create(request):
    """Grant a permission to a group"""
    if request.method == 'POST':
        form = GroupAppPermissionForm(request.POST, current_user=request.user)
        if form.is_valid():
            group_permission = form.save()
            
            # Log the action
            AccessLog.objects.create(
                user=request.user,
                target_group=group_permission.group,
                permission=group_permission.permission,
                action='grant',
                notes=f"Granted {group_permission.permission} to group {group_permission.group.name}"
            )
            
            messages.success(request, f'Permission granted to group {group_permission.group.name} successfully.')
            return redirect('access_control:group_permission_list')
    else:
        form = GroupAppPermissionForm(current_user=request.user)
    
    context = {
        'form': form,
        'title': 'Grant Permission to Group',
    }
    return render(request, 'access_control/group_permission_form.html', context)

@login_required
@user_passes_test(is_admin)
def group_permission_revoke(request, pk):
    """Revoke a permission from a group"""
    group_permission = get_object_or_404(GroupAppPermission, pk=pk)
    
    if request.method == 'POST':
        group_name = group_permission.group.name
        permission_name = group_permission.permission.name
        
        # Log the action before deleting
        AccessLog.objects.create(
            user=request.user,
            target_group=group_permission.group,
            permission=group_permission.permission,
            action='revoke',
            notes=f"Revoked {permission_name} from group {group_name}"
        )
        
        group_permission.delete()
        messages.success(request, f'Permission revoked from group {group_name} successfully.')
        return redirect('access_control:group_permission_list')
    
    context = {
        'group_permission': group_permission,
    }
    return render(request, 'access_control/group_permission_confirm_revoke.html', context)

@login_required
@user_passes_test(is_admin)
def bulk_permission_grant(request):
    """Grant permissions to multiple users or groups at once"""
    if request.method == 'POST':
        form = BulkPermissionForm(request.POST)
        if form.is_valid():
            users = form.cleaned_data.get('users', [])
            groups = form.cleaned_data.get('groups', [])
            permissions = form.cleaned_data.get('permissions', [])
            
            with transaction.atomic():
                # Grant permissions to users
                for user in users:
                    for permission in permissions:
                        # Check if permission already exists
                        if not UserAppPermission.objects.filter(user=user, permission=permission).exists():
                            user_permission = UserAppPermission.objects.create(
                                user=user,
                                permission=permission,
                                granted_by=request.user
                            )
                            
                            # Log the action
                            AccessLog.objects.create(
                                user=request.user,
                                target_user=user,
                                permission=permission,
                                action='grant',
                                notes=f"Granted {permission} to {user.username} (bulk)"
                            )
                
                # Grant permissions to groups
                for group in groups:
                    for permission in permissions:
                        # Check if permission already exists
                        if not GroupAppPermission.objects.filter(group=group, permission=permission).exists():
                            group_permission = GroupAppPermission.objects.create(
                                group=group,
                                permission=permission,
                                granted_by=request.user
                            )
                            
                            # Log the action
                            AccessLog.objects.create(
                                user=request.user,
                                target_group=group,
                                permission=permission,
                                action='grant',
                                notes=f"Granted {permission} to group {group.name} (bulk)"
                            )
            
            user_count = len(users)
            group_count = len(groups)
            perm_count = len(permissions)
            messages.success(request, f'Granted {perm_count} permissions to {user_count} users and {group_count} groups.')
            return redirect('access_control:dashboard')
    else:
        form = BulkPermissionForm()
    
    context = {
        'form': form,
        'title': 'Bulk Grant Permissions',
    }
    return render(request, 'access_control/bulk_permission_form.html', context)

@login_required
@user_passes_test(is_admin)
def access_log_list(request):
    """List all access logs"""
    logs = AccessLog.objects.all()
    
    # Filter by user if provided
    user_id = request.GET.get('user')
    if user_id:
        logs = logs.filter(user_id=user_id)
    
    # Filter by target user if provided
    target_user_id = request.GET.get('target_user')
    if target_user_id:
        logs = logs.filter(target_user_id=target_user_id)
    
    # Filter by target group if provided
    target_group_id = request.GET.get('target_group')
    if target_group_id:
        logs = logs.filter(target_group_id=target_group_id)
    
    # Filter by action if provided
    action = request.GET.get('action')
    if action:
        logs = logs.filter(action=action)
    
    # Pagination
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get users and groups for filters
    users = User.objects.all()
    groups = Group.objects.all()
    
    context = {
        'page_obj': page_obj,
        'users': users,
        'groups': groups,
        'action_types': AccessLog.ACTION_TYPES,
        'selected_user': user_id,
        'selected_target_user': target_user_id,
        'selected_target_group': target_group_id,
        'selected_action': action,
    }
    return render(request, 'access_control/access_log_list.html', context)

@login_required
@user_passes_test(is_admin)
def user_permissions_manage(request, user_id):
    """Manage all permissions for a specific user"""
    user = get_object_or_404(User, pk=user_id)
    
    if request.method == 'POST':
        form = PermissionRevokeForm(request.POST, user=user)
        if form.is_valid():
            permissions_to_revoke = form.cleaned_data.get('user_permissions', [])
            
            with transaction.atomic():
                for user_permission in permissions_to_revoke:
                    # Log the action before deleting
                    AccessLog.objects.create(
                        user=request.user,
                        target_user=user,
                        permission=user_permission.permission,
                        action='revoke',
                        notes=f"Revoked {user_permission.permission} from {user.username}"
                    )
                    
                    user_permission.delete()
            
            revoke_count = len(permissions_to_revoke)
            messages.success(request, f'Revoked {revoke_count} permissions from {user.username}.')
            return redirect('access_control:user_permissions_manage', user_id=user.id)
    else:
        form = PermissionRevokeForm(user=user)
    
    # Get all permissions for this user
    user_permissions = UserAppPermission.objects.filter(user=user)
    
    # Form for adding a new permission
    add_form = UserAppPermissionForm(current_user=request.user, initial={'user': user})
    
    context = {
        'user_obj': user,
        'user_permissions': user_permissions,
        'form': form,
        'add_form': add_form,
    }
    return render(request, 'access_control/user_permissions_manage.html', context)

@login_required
@user_passes_test(is_admin)
def group_permissions_manage(request, group_id):
    """Manage all permissions for a specific group"""
    group = get_object_or_404(Group, pk=group_id)
    
    if request.method == 'POST':
        form = PermissionRevokeForm(request.POST, group=group)
        if form.is_valid():
            permissions_to_revoke = form.cleaned_data.get('group_permissions', [])
            
            with transaction.atomic():
                for group_permission in permissions_to_revoke:
                    # Log the action before deleting
                    AccessLog.objects.create(
                        user=request.user,
                        target_group=group,
                        permission=group_permission.permission,
                        action='revoke',
                        notes=f"Revoked {group_permission.permission} from group {group.name}"
                    )
                    
                    group_permission.delete()
            
            revoke_count = len(permissions_to_revoke)
            messages.success(request, f'Revoked {revoke_count} permissions from group {group.name}.')
            return redirect('access_control:group_permissions_manage', group_id=group.id)
    else:
        form = PermissionRevokeForm(group=group)
    
    # Get all permissions for this group
    group_permissions = GroupAppPermission.objects.filter(group=group)
    
    # Form for adding a new permission
    add_form = GroupAppPermissionForm(current_user=request.user, initial={'group': group})
    
    context = {
        'group': group,
        'group_permissions': group_permissions,
        'form': form,
        'add_form': add_form,
    }
    return render(request, 'access_control/group_permissions_manage.html', context)

# API views for checking permissions
@login_required
def check_permission(request):
    """API endpoint to check if a user has a specific permission"""
    app_name = request.GET.get('app')
    feature = request.GET.get('feature')
    permission_type = request.GET.get('type', 'view')
    
    if not app_name:
        return JsonResponse({'error': 'App name is required'}, status=400)
    
    # Check if user is superuser (has all permissions)
    if request.user.is_superuser:
        return JsonResponse({'has_permission': True})
    
    # Check user permissions
    user_has_permission = UserAppPermission.objects.filter(
        user=request.user,
        permission__app_name=app_name,
        permission__feature=feature if feature else None,
        permission__permission_type__in=[permission_type, 'full'],
        permission__is_active=True
    ).exists()
    
    if user_has_permission:
        return JsonResponse({'has_permission': True})
    
    # Check group permissions
    user_groups = request.user.groups.all()
    group_has_permission = GroupAppPermission.objects.filter(
        group__in=user_groups,
        permission__app_name=app_name,
        permission__feature=feature if feature else None,
        permission__permission_type__in=[permission_type, 'full'],
        permission__is_active=True
    ).exists()
    
    return JsonResponse({'has_permission': group_has_permission})

@login_required
@user_passes_test(is_admin)
def settings(request):
    """Settings page for access control"""
    context = {
        'title': 'Access Control Settings',
    }
    return render(request, 'access_control/settings.html', context) 