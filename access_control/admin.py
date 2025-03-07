from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin, GroupAdmin as BaseGroupAdmin
from .models import AppPermission, UserAppPermission, GroupAppPermission, AccessLog

class UserAppPermissionInline(admin.TabularInline):
    model = UserAppPermission
    extra = 1
    autocomplete_fields = ['permission', 'granted_by']
    verbose_name = "App Permission"
    verbose_name_plural = "App Permissions"
    fk_name = 'user'

class GroupAppPermissionInline(admin.TabularInline):
    model = GroupAppPermission
    extra = 1
    autocomplete_fields = ['permission', 'granted_by']
    verbose_name = "App Permission"
    verbose_name_plural = "App Permissions"

class UserAdmin(BaseUserAdmin):
    inlines = BaseUserAdmin.inlines + (UserAppPermissionInline,)

class GroupAdmin(BaseGroupAdmin):
    inlines = (GroupAppPermissionInline,)

# Unregister the original User and Group admins
admin.site.unregister(User)
admin.site.unregister(Group)

# Register our custom User and Group admins
admin.site.register(User, UserAdmin)
admin.site.register(Group, GroupAdmin)

@admin.register(AppPermission)
class AppPermissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'app_name', 'feature', 'permission_type', 'is_active')
    list_filter = ('app_name', 'permission_type', 'is_active')
    search_fields = ('name', 'app_name', 'feature', 'description')
    ordering = ('app_name', 'feature', 'permission_type')
    fieldsets = (
        (None, {
            'fields': ('name', 'app_name', 'feature', 'permission_type')
        }),
        ('Details', {
            'fields': ('description', 'is_active')
        }),
    )

@admin.register(UserAppPermission)
class UserAppPermissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'permission', 'granted_by', 'granted_at')
    list_filter = ('permission__app_name', 'permission__permission_type', 'granted_at')
    search_fields = ('user__username', 'permission__name', 'granted_by__username')
    autocomplete_fields = ['user', 'permission', 'granted_by']
    date_hierarchy = 'granted_at'

@admin.register(GroupAppPermission)
class GroupAppPermissionAdmin(admin.ModelAdmin):
    list_display = ('group', 'permission', 'granted_by', 'granted_at')
    list_filter = ('permission__app_name', 'permission__permission_type', 'granted_at')
    search_fields = ('group__name', 'permission__name', 'granted_by__username')
    autocomplete_fields = ['group', 'permission', 'granted_by']
    date_hierarchy = 'granted_at'

@admin.register(AccessLog)
class AccessLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'action', 'user', 'target_display', 'permission')
    list_filter = ('action', 'timestamp', 'permission__app_name')
    search_fields = ('user__username', 'target_user__username', 'target_group__name', 'permission__name', 'notes')
    readonly_fields = ('timestamp', 'user', 'target_user', 'target_group', 'permission', 'action', 'notes')
    date_hierarchy = 'timestamp'
    
    def target_display(self, obj):
        return obj.target_user.username if obj.target_user else obj.target_group.name
    target_display.short_description = 'Target'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
