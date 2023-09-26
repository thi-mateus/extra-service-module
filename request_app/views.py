from django.shortcuts import get_object_or_404, render, redirect, reverse
from django.views.generic import ListView, DetailView
from django.views import View
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import F
from datetime import datetime
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db import transaction

from service_app.models import Service
from profile_app.models import Military, Scheduling
from .models import Request
from .utils import get_service_data, get_request_data


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
            queryset = Request.objects.all().order_by('id_sv__data_inicio')
            return queryset

        else:
            # Militar - Retorna as solicitações apenas do militar logado
            military_instance = Military.objects.get(
                usuario=self.request.user)

            queryset = Request.objects.filter(
                id_mil=military_instance, status='S'
            ).annotate(
                service_data_inicio=F('id_sv__data_inicio')
            ).order_by(
                'service_data_inicio'
            )

            return queryset

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
    context_object_name = 'classification_list'
    paginate_by = 25
    # Redirecionar para a página de login de admin caso o usuário não seja administrador
    login_url = '/admin/'

    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):
        listar_todos = self.kwargs.get('listar_todos', 0)
        listar_todos = int(listar_todos)
        services = Service.objects.all()

        if not listar_todos:
            classification_list = get_request_data(
                services, listar_todos=False)
        else:
            classification_list = get_request_data(services, listar_todos=True)

        return classification_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['listar_todos'] = int(self.kwargs.get(
            'listar_todos', 0))  # Converte para inteiro
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('/admin/')

        listar_todos = int(self.kwargs.get('listar_todos', 0))

        if listar_todos:
            # Obtenha todos os serviços
            services = Service.objects.all()

            for service in services:
                # Obtenha a lista de militares selecionados para este serviço com base no nome do campo de checkbox dinâmico
                selected_militaries_ids = request.POST.getlist(str(service.id))
                # Obtenha os objetos de militar correspondentes aos IDs selecionados
                selected_militaries = Military.objects.filter(
                    pk__in=selected_militaries_ids)

                # Obtenha a lista de militares originalmente associados a este serviço
                original_militaries = service.militares.all()

                # Adicione militares selecionados que não estejam associados ao serviço
                for military in selected_militaries:
                    if military not in original_militaries:
                        service.militares.add(military)
                        req = Request.objects.filter(
                            id_sv=service, id_mil=military).first()
                        req.status = 'A'
                        req.save()

                # Remova militares que não foram selecionados (caixa de seleção desmarcada)
                for military in original_militaries:
                    if military not in selected_militaries:
                        service.militares.remove(military)
                        req = Request.objects.filter(
                            id_sv=service, id_mil=military).first()
                        req.status = 'S'
                        req.save()
        else:
            # Lógica para processar quando listar_todos=0
            queryset = self.get_queryset()  # Obtenha o queryset
            services = [entry['service'] for entry in queryset]

            for entry in queryset:
                # Obtenha os militares correspondentes à solicitação
                requests = entry['request']
                military_ids = [req['request'].id_mil.id for req in requests]
                selected_militaries = Military.objects.filter(
                    pk__in=military_ids)

                # Associe os militares aos serviços correspondentes
                service = entry['service']
                for military in selected_militaries:
                    if military not in service.militares.all():
                        service.militares.add(military)
                        req = Request.objects.filter(
                            id_sv=service, id_mil=military).first()
                        req.status = 'A'
                        req.save()

        return redirect(reverse('request:classificacao_por_criterios', kwargs={'listar_todos': listar_todos}))


class SelecionarMilitares(UserPassesTestMixin, ListView):
    template_name = 'request/selecionados.html'
    model = Military
    context_object_name = 'service_data'
    paginate_by = 25
    # Redirecionar para a página de login de admin caso o usuário não seja administrador
    login_url = '/admin/'

    def test_func(self):
        return self.request.user.is_staff

    def post(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('/admin/')

        # Processar service_data como desejar
        # ...

        return redirect('request:selecionados')

    def get_queryset(self):
        services = Service.objects.all()
        service_data = get_service_data(services, listar_todos=False)
        return service_data


class Detail(UserPassesTestMixin, ListView):
    template_name = 'request/detail.html'
    model = Military
    context_object_name = 'classification_list'
    paginate_by = 25
    # Redirecionar para a página de login de admin caso o usuário não seja administrador
    login_url = '/admin/'

    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):
        listar_todos = self.kwargs.get('listar_todos', 0)
        listar_todos = int(listar_todos)
        services = Service.objects.all()

        if not listar_todos:
            classification_list = get_request_data(
                services, listar_todos=False)
        else:
            classification_list = get_request_data(services, listar_todos=True)

        return classification_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['listar_todos'] = int(self.kwargs.get(
            'listar_todos', 0))  # Converte para inteiro
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('/admin/')
        listar_todos = int(self.kwargs.get('listar_todos', 0))

        # Obtenha todos os serviços
        services = Service.objects.all()

        for service in services:
            # Obtenha a lista de militares selecionados para este serviço com base no nome do campo de checkbox dinâmico
            selected_militaries_ids = request.POST.getlist(str(service.id))

            # Verifique se há militares selecionados para este serviço
            if selected_militaries_ids:
                # Obtenha os objetos de militar correspondentes aos IDs selecionados
                selected_militaries = Military.objects.filter(
                    pk__in=selected_militaries_ids)

                # Itere sobre os militares selecionados
                for military in selected_militaries:
                    # Verifique se o militar não está associado ao serviço
                    if military not in service.militares.all():
                        # Se o militar não estiver associado ao serviço, adicione-o
                        service.militares.add(military)

                # Atualize o status das solicitações para 'Agendado' (A)
                Request.objects.filter(
                    id_mil__in=selected_militaries, id_sv=service).update(status='A')

        return redirect('request:selecionados')
