from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views import View
from django.http import HttpResponse
from django.contrib import messages
from django.core.serializers import serialize
from . import models


from pprint import pprint


class ListServices(ListView):
    model = models.Service
    template_name = 'service/list.html'
    context_object_name = 'services'
    paginate_by = 10


class DetailService(DetailView):
    model = models.Service
    template_name = 'service/detail.html'
    context_object_name = 'service'
    slug_url_kwarg = 'slug'


class AddToCart(View):
    def get(self, *args, **kwargs):
        # if self.request.session.get('cart'):
        #     del self.request.session['cart']
        #     self.request.session.save()

        http_referer = self.request.META.get(
            'HTTP_REFERER',
            reverse('service:list')
        )
        service_id = self.request.GET.get('sid')

        if not service_id:
            messages.error(
                self.request,
                'Serviço não existe'
            )
            return redirect(http_referer)

        service = get_object_or_404(models.Service, id=service_id)

        service_local = service.local
        service_hora_inicio = service.hora_inicio.strftime("%H:%M")
        service_data_inicio = service.data_inicio.strftime("%d/%m/%Y")
        service_hora_termino = service.hora_termino.strftime("%H:%M")
        service_data_termino = service.data_termino.strftime("%d/%m/%Y")
        service_vagas = service.vagas
        service_qtd = 1
        service_observacao = service.observacao
        service_image = service.image

        if service_image:
            service_image = service_image.name
        else:
            service_image = ''

        service_slug = service.slug
        service_militares = serialize('json', service.militares.all())

        if service.vagas < 1:
            messages.error(
                self.request,
                'Vagas Insuficientes'
            )
            return redirect(http_referer)

        if not self.request.session.get('cart'):
            self.request.session['cart'] = {}
            self.request.session.save()

        cart = self.request.session['cart']

        if service_id in cart:
            qtd_cart = cart[service_id]['service_qtd']
            qtd_cart += 1

            if service_vagas < qtd_cart:
                messages.error(
                    self.request,
                    f'Vagas Insuficientes para {qtd_cart}x no '
                    f'serviço "{service.local}-{service.data_inicio.strftime("%d/%m/%Y")}"'
                )
                qtd_cart = service.vagas

            cart[service_id]['service_qtd'] = qtd_cart

        else:
            cart[service_id] = {
                'service_id': service_id,
                'service_local': service_local,
                'service_hora_inicio': service_hora_inicio,
                'service_data_inicio': service_data_inicio,
                'service_hora_termino': service_hora_termino,
                'service_data_termino': service_data_termino,
                'service_vagas': service_vagas,
                'service_observacao': service_observacao,
                'service_image': service_image,
                'service_slug': service_slug,
                'service_militares': service_militares,
            }

        self.request.session.save()
        pprint(cart)
        return HttpResponse(f'{service.local} {service.data_inicio}')


class RemoveFromCart(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Remove from cart')


class Cart(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Cart')


class Finish(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Finish')
