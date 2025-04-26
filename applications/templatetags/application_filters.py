from django import template

register = template.Library()

@register.filter
def split(value, arg):
    """
    Split the value by the argument
    """
    # Check if value is already a list
    if isinstance(value, list):
        return value
    # Handle None values
    if value is None:
        return []
    # Convert to string and split
    return str(value).split(arg)

@register.filter
def trim(value):
    """
    Trim whitespace from the beginning and end of a string
    """
    if value is None:
        return ""
    return str(value).strip()