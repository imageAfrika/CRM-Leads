from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Lead, LeadActivity


@receiver(post_save, sender=Lead)
def create_lead_activity(sender, instance, created, **kwargs):
    """Create a lead activity when a lead is created or its status changes."""
    if created:
        LeadActivity.objects.create(
            lead=instance,
            activity_type='created',
            description='Lead created',
            created_by=instance.created_by
        )
    else:
        # Check if status has changed
        if instance.tracker.has_changed('status'):
            old_status = instance.tracker.previous('status')
            new_status = instance.status
            LeadActivity.objects.create(
                lead=instance,
                activity_type='status_change',
                description=f'Status changed from {old_status} to {new_status}',
                created_by=instance.modified_by
            )

        # Check if assigned_to has changed
        if instance.tracker.has_changed('assigned_to'):
            old_assigned = instance.tracker.previous('assigned_to')
            new_assigned = instance.assigned_to
            LeadActivity.objects.create(
                lead=instance,
                activity_type='assignment',
                description=f'Lead assigned from {old_assigned} to {new_assigned}',
                created_by=instance.modified_by
            ) 