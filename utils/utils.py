WEEKDAYS = ["Segunda-feira", "Terça-feira", "Quarta-feira",
            "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]


def format_date_service(date):
    return date.strftime("%d/%m/%Y")


def format_time_service(time):
    return time.strftime("%H:%M")


def weekday_name(date):
    return WEEKDAYS[date.weekday()]
