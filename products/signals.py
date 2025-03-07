from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
import json

from .models import (
    Product, 
    Category, 
    InventoryTransaction, 
    Supplier, 
    Purchase, 
    PurchaseItem,
    AuditLog
)

def get_changes(old_instance, new_instance):
    """Compare old and new instances to get changes"""
    if not old_instance:
        return None
    
    old_dict = model_to_dict(old_instance)
    new_dict = model_to_dict(new_instance)
    changes = {}
    
    for key, old_value in old_dict.items():
        if key in new_dict and old_value != new_dict[key]:
            changes[key] = {
                'old': str(old_value),
                'new': str(new_dict[key])
            }
    
    return changes if changes else None

def create_audit_log(sender, instance, user, action, changes=None):
    """Create an audit log entry"""
    if not user or not isinstance(user, User):
        # Try to get user from instance
        if hasattr(instance, 'updated_by') and instance.updated_by:
            user = instance.updated_by
        elif hasattr(instance, 'created_by') and instance.created_by:
            user = instance.created_by
        else:
            # Use a system user or admin if no user is available
            user = User.objects.filter(is_superuser=True).first()
    
    AuditLog.objects.create(
        user=user,
        action=action,
        model_name=sender.__name__,
        object_id=str(instance.pk),
        object_repr=str(instance),
        changes=changes
    )

# Dictionary to store pre-save instances for comparison
pre_save_instances = {}

@receiver(pre_save)
def store_pre_save_instance(sender, instance, **kwargs):
    """Store instance before save for comparison"""
    if sender in [Product, Category, Supplier, Purchase]:
        if instance.pk:  # Only for existing instances
            try:
                pre_save_instances[f"{sender.__name__}_{instance.pk}"] = sender.objects.get(pk=instance.pk)
            except sender.DoesNotExist:
                pass

@receiver(post_save)
def log_post_save(sender, instance, created, **kwargs):
    """Log after an object is created or updated"""
    if sender in [Product, Category, Supplier, Purchase]:
        action = 'create' if created else 'update'
        user = instance.created_by if created else instance.updated_by
        
        changes = None
        if not created:
            # Get the pre-save instance for comparison
            pre_save_key = f"{sender.__name__}_{instance.pk}"
            if pre_save_key in pre_save_instances:
                old_instance = pre_save_instances.pop(pre_save_key)
                changes = get_changes(old_instance, instance)
        
        create_audit_log(sender, instance, user, action, changes)

@receiver(post_delete)
def log_post_delete(sender, instance, **kwargs):
    """Log after an object is deleted"""
    if sender in [Product, Category, Supplier, Purchase]:
        user = instance.updated_by if hasattr(instance, 'updated_by') else None
        create_audit_log(sender, instance, user, 'delete')

@receiver(post_save, sender=InventoryTransaction)
def log_inventory_transaction(sender, instance, created, **kwargs):
    """Log inventory transactions"""
    if created:
        create_audit_log(
            sender, 
            instance, 
            instance.created_by, 
            'create',
            {
                'product': str(instance.product),
                'transaction_type': instance.transaction_type,
                'quantity': str(instance.quantity),
                'unit_price': str(instance.unit_price),
                'total_amount': str(instance.total_amount)
            }
        ) 