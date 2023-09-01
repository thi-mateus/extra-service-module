from django.shortcuts import get_object_or_404, render, redirect, reverse
from django.views.generic import ListView, DetailView
from django.views import View
from django.http import HttpResponse
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from service_app.models import Service
from profile_app.models import Military
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
        military_instance = Military.objects.get(
            usuario=self.request.user)
        return Request.objects.filter(
            id_mil=military_instance, status='S').order_by(
                '-data_solicitacao')

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


class List(View):
    def get(self, *args, **kwargs):
        return HttpResponse('List')


class Detail(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Detail')
