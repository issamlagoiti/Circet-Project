from django import template
import json

register = template.Library()

@register.filter
def date_labels(parcours_per_month):
    return json.dumps([str(day) for day, count in parcours_per_month])

@register.filter
def count_data(parcours_per_month):
    return json.dumps([count for day, count in parcours_per_month])
