from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import ListView
from django.views import View
from django.http import HttpResponse
from django.contrib import messages

from service_app.models import Service
from profile_app.models import Military
from .models import Request
from datetime import datetime
import pytz


class Send(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Finalize Request')


class SaveRequest(View):
    template_name = 'request/send.html'

    def get(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            messages.error(
                self.request,
                'Você precisa fazer login.'
            )
            return redirect('profile:create')

        if not self.request.session.get('cart'):
            messages.error(
                self.request,
                'Não há solicitação de serviço.'
            )
            return redirect('service:list')

        cart = self.request.session.get('cart')
        cart_service_ids = [sv for sv in cart]
        db_service = list(
            Service.objects.filter(id__in=cart_service_ids)
        )

        for service in db_service:
            sid = str(service.id)
            status = cart[sid]['service_status']

            # Verificar se o serviço que está no carrinho ainda está aberto(A)
            if service.status != 'A':

                messages.error(
                    self.request,
                    f'O serviço "{cart[sid]["service_local"]} - {cart[sid]["service_data_inicio"]}" '
                    f'não está mais aberto para solicitações.'
                )
                # Serviço não está aberto(A): deletar do carrinho!
                del self.request.session['cart'][sid]
                self.request.session.save()

                return redirect('service:cart')

        Request.objects.bulk_create(
            [
                Request(
                    id_mil=Military.objects.filter(
                        usuario=self.request.user).first(),
                    id_sv=get_object_or_404(
                        Service, id=v['service_id']),
                    id_opcao=1,
                    data_solicitacao=pytz.timezone(
                        'America/Sao_Paulo').localize(datetime.now()),
                    status='S',
                    criterio='',
                ) for v in cart.values()
            ]
        )

        del self.request.session['cart']
        # return render(self.request, self.template_name, context)
        return redirect('request:list')


class List(View):
    def get(self, *args, **kwargs):
        return HttpResponse('List')


class Detail(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Detail')
