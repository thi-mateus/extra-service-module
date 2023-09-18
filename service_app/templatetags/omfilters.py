from django.template import Library
from utils import utils


register = Library()


@register.filter
def format_date(date):
    return utils.format_date(date)


@register.filter
def format_time(time):
    return utils.format_time(time)


@register.filter
def format_datetime(datetime):
    return utils.format_datetime(datetime)


@register.filter
def weekday_name(date):
    return utils.weekday_name(date)


@register.filter
def cart_total_qtd(cart):
    return utils.cart_total_qtd(cart)


@register.filter
def toggle_direction(direction, column):
    return utils.toggle_direction(direction, column)


@register.filter
def get_attribute(obj, attr_name):
    return utils.get_attribute(obj, attr_name)
