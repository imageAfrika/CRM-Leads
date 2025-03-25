from django.contrib import admin
from .models import AdminLog


@admin.register(AdminLog)
class AdminLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'timestamp', 'content_type', 'object_repr', 'action_type', 'app_label', 'model_name')
    list_filter = ('user', 'timestamp', 'content_type', 'action_type', 'app_label', 'model_name')
    search_fields = ('user__username', 'object_repr', 'details')
    date_hierarchy = 'timestamp'
    readonly_fields = ('user', 'content_type', 'object_id', 'object_repr', 
                       'action_type', 'timestamp', 'app_label', 'model_name', 'details')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
