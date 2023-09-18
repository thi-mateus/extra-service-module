from django.utils import timezone


WEEKDAYS = ["Segunda-feira", "Terça-feira", "Quarta-feira",
            "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]


def format_date(date):
    return date.strftime("%d/%m/%Y")


def format_time(time):
    return time.strftime("%H:%M")


def format_datetime(datetime):
    local_datetime = datetime.astimezone(timezone.get_current_timezone())
    formatted_datetime = local_datetime.strftime("%d/%m/%Y %H:%M")
    return formatted_datetime


def weekday_name(date):
    return WEEKDAYS[date.weekday()]


def cart_total_qtd(cart):
    return sum([item['service_qtd'] for item in cart.values()])


def toggle_direction(direction, column):
    if direction.startswith('-') and direction.lstrip('-') == column:
        return column
    else:
        return f'-{column}'


def get_attribute(obj, attr_name):
    try:
        return getattr(obj, attr_name)
    except AttributeError:
        return None
