from django.template import Library
from utils import utils

register = Library()


@register.filter
def format_date_service(date):
    return utils.format_date_service(date)


@register.filter
def weekday_name(date):
    return utils.weekday_name(date)


@register.filter
def cart_total_qtd(cart):
    return utils.cart_total_qtd(cart)
