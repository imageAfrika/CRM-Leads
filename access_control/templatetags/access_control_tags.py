from django import template
from django.contrib.auth.models import User, Group

from access_control.models import UserAppPermission, GroupAppPermission

register = template.Library()

@register.simple_tag
def has_permission(user, app_name, permission_type='view', feature=None):
    """
    Check if a user has permission to access a feature
    
    Usage:
        {% load access_control_tags %}
        {% has_permission user 'app_name' 'permission_type' 'feature' as has_perm %}
        {% if has_perm %}
            <!-- Show content -->
        {% endif %}
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

@register.filter
def has_app_permission(user, app_name):
    """
    Check if a user has any permission for an app
    
    Usage:
        {% load access_control_tags %}
        {% if user|has_app_permission:'app_name' %}
            <!-- Show app in menu -->
        {% endif %}
    """
    # Skip check for superusers
    if user.is_superuser:
        return True
    
    # Check if user has direct permission
    user_has_permission = UserAppPermission.objects.filter(
        user=user,
        permission__app_name=app_name,
        permission__is_active=True
    ).exists()
    
    if user_has_permission:
        return True
    
    # Check if user has permission through a group
    user_groups = user.groups.all()
    group_has_permission = GroupAppPermission.objects.filter(
        group__in=user_groups,
        permission__app_name=app_name,
        permission__is_active=True
    ).exists()
    
    return group_has_permission

@register.filter
def has_feature_permission(user, feature_string):
    """
    Check if a user has permission for a specific feature
    
    Usage:
        {% load access_control_tags %}
        {% if user|has_feature_permission:'app_name:feature:permission_type' %}
            <!-- Show feature -->
        {% endif %}
    """
    # Parse feature string
    parts = feature_string.split(':')
    if len(parts) < 2:
        return False
    
    app_name = parts[0]
    feature = parts[1]
    permission_type = parts[2] if len(parts) > 2 else 'view'
    
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