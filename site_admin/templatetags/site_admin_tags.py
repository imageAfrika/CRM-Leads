from django import template
from django.utils.html import format_html

register = template.Library()


@register.filter
def getattr(obj, attr_name):
    """
    Gets an attribute value from an object dynamically.
    
    Usage: {{ object|getattr:"attribute_name" }}
    """
    try:
        attr_value = getattr(obj, attr_name, None)
        
        # Handle callable attributes (methods)
        if callable(attr_value):
            return attr_value()
            
        # Handle None values
        if attr_value is None:
            return "-"
            
        # Handle boolean values
        if isinstance(attr_value, bool):
            if attr_value:
                return format_html('<span class="badge badge-success">Yes</span>')
            else:
                return format_html('<span class="badge badge-danger">No</span>')
                
        return attr_value
    except Exception:
        return "-"

@register.simple_tag
def has_model_permission(user, app_label, model_name, permission_type):
    """
    Check if a user has the specified permission for a model.
    
    Usage: {% has_model_permission user "app_label" "model_name" "view" %}
    """
    if user.is_superuser:
        return True
        
    permission_codename = f"{permission_type}_{model_name}"
    return user.has_perm(f"{app_label}.{permission_codename}")

@register.filter
def verbose_name(model):
    """
    Returns the verbose_name of a model.
    
    Usage: {{ model|verbose_name }}
    """
    try:
        return model._meta.verbose_name
    except AttributeError:
        return model.__name__

@register.filter
def verbose_name_plural(model):
    """
    Returns the verbose_name_plural of a model.
    
    Usage: {{ model|verbose_name_plural }}
    """
    try:
        return model._meta.verbose_name_plural
    except AttributeError:
        return f"{model.__name__}s"
