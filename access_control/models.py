from django.db import models
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.apps import apps

class AppPermission(models.Model):
    """
    Custom permission model for controlling access to specific apps and features
    """
    PERMISSION_TYPES = (
        ('view', 'View'),
        ('add', 'Add'),
        ('change', 'Change'),
        ('delete', 'Delete'),
        ('full', 'Full Access'),
    )
    
    name = models.CharField(max_length=255)
    app_name = models.CharField(max_length=100)
    feature = models.CharField(max_length=100, blank=True, null=True, 
                              help_text="Specific feature within the app (e.g., 'reports', 'dashboard')")
    permission_type = models.CharField(max_length=20, choices=PERMISSION_TYPES)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('app_name', 'feature', 'permission_type')
        ordering = ['app_name', 'feature', 'permission_type']
        verbose_name = 'App Permission'
        verbose_name_plural = 'App Permissions'
    
    def __str__(self):
        feature_str = f" - {self.feature}" if self.feature else ""
        return f"{self.app_name}{feature_str} ({self.get_permission_type_display()})"
    
    @classmethod
    def get_available_apps(cls):
        """Return a list of all installed apps that can be managed"""
        excluded_apps = ['admin', 'auth', 'contenttypes', 'sessions', 'messages', 'staticfiles']
        return [app for app in apps.get_app_configs() if app.name not in excluded_apps]

class UserAppPermission(models.Model):
    """
    Assigns app permissions to specific users
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='app_permissions')
    permission = models.ForeignKey(AppPermission, on_delete=models.CASCADE, related_name='user_permissions')
    granted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='access_granted_permissions')
    granted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'permission')
        ordering = ['user', 'permission']
        verbose_name = 'User App Permission'
        verbose_name_plural = 'User App Permissions'
    
    def __str__(self):
        return f"{self.user.username} - {self.permission}"

class GroupAppPermission(models.Model):
    """
    Assigns app permissions to groups
    """
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='app_permissions')
    permission = models.ForeignKey(AppPermission, on_delete=models.CASCADE, related_name='group_permissions')
    granted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='granted_group_permissions')
    granted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('group', 'permission')
        ordering = ['group', 'permission']
        verbose_name = 'Group App Permission'
        verbose_name_plural = 'Group App Permissions'
    
    def __str__(self):
        return f"{self.group.name} - {self.permission}"

class AccessLog(models.Model):
    """
    Logs permission changes for audit purposes
    """
    ACTION_TYPES = (
        ('grant', 'Permission Granted'),
        ('revoke', 'Permission Revoked'),
        ('modify', 'Permission Modified'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='access_changes')
    target_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='access_logs', null=True, blank=True)
    target_group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='access_logs', null=True, blank=True)
    permission = models.ForeignKey(AppPermission, on_delete=models.CASCADE, related_name='access_logs')
    action = models.CharField(max_length=20, choices=ACTION_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Access Log'
        verbose_name_plural = 'Access Logs'
    
    def __str__(self):
        target = self.target_user.username if self.target_user else self.target_group.name
        return f"{self.get_action_display()} - {target} - {self.permission} ({self.timestamp.strftime('%Y-%m-%d %H:%M')})"
