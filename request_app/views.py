from django.shortcuts import get_object_or_404, render, redirect, reverse
from django.views.generic import ListView, DetailView
from django.views import View
from django.http import HttpResponse
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import F, Min
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
    paginate_by = 10

    def get_queryset(self):
        if self.request.user.is_staff:
            # Administrador - Retorna todas as solicitações
            return Request.objects.all()

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


class Select(UserPassesTestMixin, ListView):
    template_name = 'request/select.html'
    model = Military
    context_object_name = 'selected_militaries'
    paginate_by = 25
    # Redirecionar para a página de login de admin caso o usuário não seja administrador
    login_url = '/admin/'

    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):
        # Obtenha a data atual
        current_date = datetime.now()

        # Filtrar os militares pelo mês e ano de referência atual
        queryset = Military.objects.filter(
            scheduling__mes_referencia__year=current_date.year,
            scheduling__mes_referencia__month=current_date.month
        ).annotate(
            min_extras=Min('scheduling__qtd')
        ).order_by('min_extras', 'antiguidade')

        return queryset

    def get(self, request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied  # Lançar exceção 403 personalizada

        return super().get(request, *args, **kwargs)


class Detail(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Detail')
