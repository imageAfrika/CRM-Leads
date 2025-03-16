from django.db import models


class AdminLog(models.Model):
    """
    Store admin actions for auditing purposes.
    """
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='admin_logs')
    content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.SET_NULL, 
                                    null=True, blank=True)
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'admin log entry'
        verbose_name_plural = 'admin log entries'

    def __str__(self):
        return f"{self.user.username} - {self.get_action_flag_display()} - {self.object_repr}"

    def get_action_flag_display(self):
        flags = {
            1: 'Addition',
            2: 'Change',
            3: 'Deletion',
        }
        return flags.get(self.action_flag, 'Unknown')
