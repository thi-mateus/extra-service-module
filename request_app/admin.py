from django import forms
from django.contrib import admin
from .models import Request


class RequestAdminForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = '__all__'  # Inclua todos os campos do modelo

    def clean(self):
        cleaned_data = super().clean()
        id_mil = cleaned_data.get('id_mil')
        id_sv = cleaned_data.get('id_sv')

        # Verifique se já existe uma solicitação com a mesma combinação de id_mil e id_sv
        if Request.objects.filter(id_mil=id_mil, id_sv=id_sv).exists():
            raise forms.ValidationError(
                "Este militar já agendou este serviço.")
        return cleaned_data


class RequestAdmin(admin.ModelAdmin):
    form = RequestAdminForm


admin.site.register(Request, RequestAdmin)
