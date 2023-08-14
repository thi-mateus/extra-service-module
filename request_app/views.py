from django.shortcuts import render
from django.views.generic import ListView
from django.views import View
from django.http import HttpResponse


class Pay(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Pay')


class FinalizeRequest(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Finalize Request')


class Detail(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Detail')
