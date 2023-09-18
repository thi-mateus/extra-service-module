from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def order_by_link(column_name, display_name, current_order_by, current_direction, url_name):
    direction = 'asc'  # Padrão para ascendente

    if column_name == current_order_by:
        if current_direction == 'asc':
            direction = 'desc'
        else:
            direction = 'asc'

    url = reverse(url_name)
    icon_class = 'fa fa-sort'  # Classe padrão para ícone de ordenação

    if column_name == current_order_by:
        if current_direction == 'asc':
            icon_class = 'fa fa-caret-up'
        else:
            icon_class = 'fa fa-caret-down'

    link = f'<a href="{url}?order_by={column_name}&direction={direction}">{display_name} <i class="{icon_class}"></i></a>'

    return mark_safe(link)
