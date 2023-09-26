from django import forms
from django.contrib import admin
from .models import Request


class RequestAdminForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = '__all__'


class RequestAdmin(admin.ModelAdmin):
    form = RequestAdminForm
    list_display = ['id_mil', 'id_sv',
                    'id_opcao', 'data_solicitacao', 'status']


admin.site.register(Request, RequestAdmin)
