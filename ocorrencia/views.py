from django.views import View
from django.http import HttpResponse
from django.shortcuts import render


class Criar(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Criar')
