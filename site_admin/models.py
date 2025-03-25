from django.db import models
from django.utils import timezone
from django.db.models import JSONField


class AdminLog(models.Model):
    """
    Store admin actions for auditing purposes.
    """
    ACTION_TYPES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('view', 'View'),
        ('login', 'Login'),
        ('logout', 'Logout'),
    ]

    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='admin_logs')
    content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.SET_NULL, 
                                     null=True, blank=True)
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    
    # More detailed action tracking
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES, default='view')
    timestamp = models.DateTimeField(default=timezone.now)
    
    # Additional context
    app_label = models.CharField(max_length=100, blank=True, null=True)
    model_name = models.CharField(max_length=100, blank=True, null=True)
    
    # Optional additional details
    details = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'admin log entry'
        verbose_name_plural = 'admin log entries'

    def __str__(self):
        return f"{self.user.username} - {self.get_action_type_display()} - {self.object_repr}"

    def save(self, *args, **kwargs):
        # Ensure app_label and model_name are set if content_type is available
        if self.content_type and (not self.app_label or not self.model_name):
            self.app_label = self.content_type.app_label
            self.model_name = self.content_type.model
        
        super().save(*args, **kwargs)

    def get_action_type_display(self):
        return dict(self.ACTION_TYPES).get(self.action_type, self.action_type)
