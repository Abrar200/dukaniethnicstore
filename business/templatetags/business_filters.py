# Create this file at business/templatetags/business_filters.py

from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Template filter to get an item from a dictionary by key"""
    if dictionary is None:
        return None
    return dictionary.get(key)