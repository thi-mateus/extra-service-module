from django.shortcuts import get_object_or_404, render, redirect, reverse
from django.views.generic import ListView, DetailView
from django.views import View
from django.http import HttpResponse
from django.contrib import messages

from service_app.models import Service
from profile_app.models import Military
from .models import Request
from django.utils import timezone


class ListRequests(ListView):
    template_name = 'request/list_requests.html'
    context_object_name = 'request_list'

    def dispatch(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            messages.error(self.request, 'Você precisa fazer login.')
            return redirect('profile:create')
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        military_instance = Military.objects.filter(
            usuario=self.request.user).first()
        return Request.objects.filter(id_mil=military_instance, status='S')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        military_instance = Military.objects.filter(
            usuario=self.request.user).first()
        context['military'] = military_instance
        return context


class SaveRequest(View):
    template_name = 'request/saverequest.html'

    def dispatch(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            messages.error(self.request, 'Você precisa fazer login.')
            return redirect('profile:create')

        self.military_instance = Military.objects.filter(
            usuario=self.request.user).first()

        return super().dispatch(*args, **kwargs)

    def check_authentication(self):
        if not self.request.user.is_authenticated:
            messages.error(
                self.request,
                'Você precisa fazer login.'
            )
            return redirect('profile:create')

    def check_cart(self):
        if not self.request.session.get('cart'):
            messages.error(
                self.request,
                'Não há solicitação de serviço.'
            )
            return redirect('service:list')

    def check_service_status(self, service):
        if service.status != 'A':
            messages.error(
                self.request,
                f'O serviço "{service.local} - {service.data_inicio}" '
                f'não está mais aberto para solicitações.'
            )
            return True

    def create_requests(self, cart):
        military_instance = Military.objects.filter(
            usuario=self.request.user).first()
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

    def check_service_already_selected(self, cart, service_id):
        for cart_item in cart.values():
            if cart_item['service_id'] == service_id:
                return True

        user_requests = Request.objects.filter(
            id_mil=self.military_instance,
            id_sv=service_id
        ).exists()
        return user_requests

    def get(self, *args, **kwargs):
        self.check_authentication()
        self.check_cart()

        cart = self.request.session.get('cart')
        cart_service_ids = [sv for sv in cart]
        db_services = list(
            Service.objects.filter(id__in=cart_service_ids)
        )

        for service in db_services:
            if self.check_service_status(service):
                del self.request.session['cart'][str(service.id)]
                self.request.session.save()
                return redirect('service:cart')

            if self.check_service_already_selected(cart, service.id):
                messages.error(
                    self.request,
                    f'O serviço "{service.local} - {service.data_inicio}" '
                    f'já foi adicionado à sua solicitação.'
                )
                return redirect('request:list_requests')

        self.create_requests(cart)
        del self.request.session['cart']
        return redirect('request:list_requests')


class List(View):
    def get(self, *args, **kwargs):
        return HttpResponse('List')


class Detail(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Detail')
