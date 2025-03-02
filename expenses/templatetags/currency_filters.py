from django import template

register = template.Library()

@register.filter
def currency(value):
    """Format a number as currency."""
    if value is None:
        return ''
    return "${:,.2f}".format(value) 