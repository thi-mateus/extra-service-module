from datetime import datetime
from .models import Request
from profile_app.models import Scheduling


def get_service_data(services, listar_todos):

    # Mês e ano de referência atual
    current_date = datetime.now()

    # Lista para armazenar informações de serviço e solicitações
    service_data = []

    for service in services:
        # Para cada serviço, pegue todas as solicitações (requests)
        requests = Request.objects.filter(id_sv=service)

        # Lista para armazenar informações de solicitação
        request_data = []

        for request in requests:
            # Militar associado a esta solicitação
            military = request.id_mil

            # Filtrar as entradas de Scheduling pelo mês de referência atual e pelo militar
            scheduling = Scheduling.objects.filter(
                militar=military,
                mes_referencia__year=current_date.year,
                mes_referencia__month=current_date.month
            ).first()  # Pega a primeira entrada se houver múltiplas, ou None se não houver

            if scheduling:
                qtd = scheduling.qtd
            else:
                qtd = 0  # Valor padrão se não houver um registro em Scheduling

            # Adicione informações da solicitação, do militar e da quantidade à lista de solicitações
            request_data.append({
                'military': military,
                'qtd': qtd,
            })

        # Ordene a lista de solicitações para este serviço com base nos critérios
        request_data = sorted(request_data, key=lambda x: (
            x['qtd'], x['military'].antiguidade))

        # Obtenha o número de vagas disponíveis para este serviço
        numero_de_vagas = service.vagas

        # Se não quiser listar todos, limite os militares apresentados aos que estão dentro das vagas
        if not listar_todos:
            request_data = request_data[:numero_de_vagas]

        service_data.append({
            'service': service,
            'military_requests': request_data,
        })

    return service_data


def get_request_data(services, listar_todos):

    # Mês e ano de referência atual
    current_date = datetime.now()

    # Lista para armazenar somente requests
    classification_list = []

    for service in services:
        # Para cada serviço, pegue todas as solicitações (requests)
        requests = Request.objects.filter(id_sv=service)

        # Lista para armazenar informações de solicitação
        request_temp = []

        for request in requests:
            # Militar associado a esta solicitação
            military = request.id_mil

            # Filtrar as entradas de Scheduling pelo mês de referência atual e pelo militar
            scheduling = Scheduling.objects.filter(
                militar=military,
                mes_referencia__year=current_date.year,
                mes_referencia__month=current_date.month
            ).first()  # Pega a primeira entrada se houver múltiplas, ou None se não houver

            if scheduling:
                qtd = scheduling.qtd
            else:
                qtd = 0  # Valor padrão se não houver um registro em Scheduling

            # Adicione informações da solicitação, do militar e da quantidade à lista de solicitações

            request_temp.append({
                'request': request,
                'qtd': qtd,
            })

        # Ordene a lista de solicitações para este serviço com base nos critérios
        request_temp = sorted(request_temp, key=lambda x: (
            x['qtd'], x['request'].id_mil.antiguidade))

        # Obtenha o número de vagas disponíveis para este serviço
        numero_de_vagas = service.vagas

        # Se não quiser listar todos, limite os militares apresentados aos que estão dentro das vagas
        if not listar_todos:
            request_temp = request_temp[:numero_de_vagas]

        classification_list.append({
            'service': service,
            'request': request_temp,
        })

    return classification_list
