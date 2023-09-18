from django.shortcuts import get_object_or_404, render, redirect, reverse
from django.views.generic import ListView, DetailView
from django.views import View
from django.http import HttpResponse
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import F, Min, Count, Subquery, OuterRef
from datetime import datetime
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied

from service_app.models import Service
from profile_app.models import Military, Scheduling
from .models import Request


class RequestMixin:
    @method_decorator(login_required(login_url='profile:create'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class ListRequests(RequestMixin, ListView):
    template_name = 'request/list_requests.html'
    context_object_name = 'request_list'
    paginate_by = 25

    def get_queryset(self):
        if self.request.user.is_staff:
            # Administrador - Retorna todas as solicitações
            return Request.objects.all().order_by('id_sv__data_inicio')

        else:
            # Militar - Retorna as solicitações apenas do militar logado
            military_instance = Military.objects.get(
                usuario=self.request.user)

            return Request.objects.filter(
                id_mil=military_instance, status='S'
            ).annotate(
                service_data_inicio=F('id_sv__data_inicio')
            ).order_by(
                'service_data_inicio'
            )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        military_instance = Military.objects.get(
            usuario=self.request.user)
        context['military'] = military_instance
        return context


class SaveRequest(View):
    template_name = 'request/saverequest.html'

    @method_decorator(login_required(login_url='profile:create'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def check_cart(self):
        if not self.request.session.get('cart'):
            messages.error(
                self.request,
                'Não há solicitação de serviço.'
            )
            return redirect('service:list')

    def check_service_status_and_cart(self, service):
        if service.status != 'A':
            service_id = str(service.id)
            if service_id in self.request.session['cart']:
                del self.request.session['cart'][service_id]
                self.request.session.save()

            messages.error(
                self.request,
                f'O serviço "{service.local} - {service.data_inicio}" '
                f'não está mais aberto para solicitações.'
            )
            return True

        service_id = str(service.id)
        if self.check_service_already_selected(service_id):
            del self.request.session['cart'][service_id]
            self.request.session.save()
            messages.error(
                self.request,
                f'O serviço "{service.local} - {service.data_inicio}" '
                f'já foi adicionado à sua solicitação.'
            )
            return True

        return False

    def check_service_already_selected(self, service_id):
        military_instance = Military.objects.get(
            usuario=self.request.user)
        user_requests = Request.objects.filter(
            id_mil=military_instance,
            id_sv=service_id
        )

        if user_requests.exists():
            return user_requests

    def create_requests(self, cart):
        military_instance = Military.objects.get(
            usuario=self.request.user)
        current_timezone = timezone.get_current_timezone()

        requests_to_create = [
            Request(
                id_mil=military_instance,
                id_sv=get_object_or_404(Service, id=v['service_id']),
                id_opcao=1,
                data_solicitacao=timezone.localtime(
                    timezone.now(), current_timezone),
                status='S',
                criterio='',
            ) for v in cart.values()
        ]

        Request.objects.bulk_create(requests_to_create)

        messages.success(
            self.request,
            'A solicitação foi salva com sucesso!.'
        )

    def get(self, *args, **kwargs):
        self.check_cart()

        cart = self.request.session.get('cart')
        cart_service_ids = [sv['service_id'] for sv in cart.values()]
        db_services = list(
            Service.objects.filter(id__in=cart_service_ids)
        )

        for service in db_services:
            if self.check_service_status_and_cart(service):
                self.request.session.save()
                return redirect('service:cart')

        self.create_requests(cart)
        del self.request.session['cart']
        return redirect('request:list_requests')


class ClassificacaoPorCriterios(UserPassesTestMixin, ListView):
    template_name = 'request/classificacao_por_criterios.html'
    model = Military
    context_object_name = 'service_data'
    paginate_by = 25
    # Redirecionar para a página de login de admin caso o usuário não seja administrador
    login_url = '/admin/'

    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):
        # Todos os serviços
        services = Service.objects.all()

        # Mês e ano de referência atual
        current_date = datetime.now()

        # Lista para armazenar informações de serviço e solicitações
        service_data = []

        for service in services:
            # Para cada serviço, as solicitações correspondentes
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

            # Adicione informações do serviço e das solicitações à lista de serviços
            service_data.append({
                'service': service,
                'military_requests': request_data,
            })
        # print(service_data[0]['military_requests'][0])

        return service_data


class SelecionarMilitares(View):
    def get(self, request):
        # Recupere o service_data da sessão
        service_data = request.session.get('service_data', [])
        print(service_data)

        # Lógica para seleção de militares dentro das vagas do serviço
        # ...

        return redirect('request:classificacao_por_criterios')


class Detail(UserPassesTestMixin, ListView):
    template_name = 'request/detail.html'
    model = Military
    context_object_name = 'service_data'
    paginate_by = 25
    # Redirecionar para a página de login de admin caso o usuário não seja administrador
    login_url = '/admin/'

    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):
        # Obtenha todos os serviços
        services = Service.objects.all()

        # Obtenha o mês e ano de referência atual
        current_date = datetime.now()

        # Crie uma lista para armazenar informações de serviço e solicitações
        service_data = []

        for service in services:
            # Para cada serviço, obtenha as solicitações correspondentes
            requests = Request.objects.filter(id_sv=service)

            # Crie uma lista para armazenar informações de solicitação
            request_data = []

            for request in requests:
                # Obtenha o militar associado a esta solicitação
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
                    qtd = 0  # Ou qualquer valor padrão que você preferir se não houver um registro em Scheduling

                # Adicione informações da solicitação, do militar e da quantidade à lista de solicitações
                request_data.append({
                    'military': military,
                    'qtd': qtd,
                })

            # Adicione informações do serviço e das solicitações à lista de serviços
            service_data.append({
                'service': service,
                'military_requests': request_data,
            })

        return service_data
