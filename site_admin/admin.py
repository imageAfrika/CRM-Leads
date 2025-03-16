from django.contrib import admin
from .models import AdminLog


@admin.register(AdminLog)
class AdminLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'timestamp', 'content_type', 'object_repr', 'get_action_flag_display')
    list_filter = ('user', 'timestamp', 'content_type', 'action_flag')
    search_fields = ('user__username', 'object_repr', 'change_message')
    date_hierarchy = 'timestamp'
    readonly_fields = ('user', 'content_type', 'object_id', 'object_repr', 
                       'action_flag', 'change_message', 'timestamp')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
