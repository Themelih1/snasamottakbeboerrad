from django import template
from datetime import datetime

register = template.Library()

@register.filter
def parse_iso_datetime(value):
    if not value:
        return ""
    try:
        # Handle both 'Z' timezone and offset formats
        dt_str = value.replace('Z', '+00:00') if 'Z' in value else value
        return datetime.fromisoformat(dt_str)
    except (AttributeError, ValueError, TypeError):
        return None