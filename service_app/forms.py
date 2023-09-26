from django import forms
from .models import Service
from profile_app.models import Military


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = '__all__'
        widgets = {
            'data_inicio': forms.DateInput(attrs={'type': 'date'}),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time'}),
            'data_termino': forms.DateInput(attrs={'type': 'date'}),
            'hora_termino': forms.TimeInput(attrs={'type': 'time'}),
        }

    militares = forms.ModelMultipleChoiceField(
        queryset=Military.objects.all(),  # Substitua por seu próprio queryset
        widget=forms.CheckboxSelectMultiple,
        required=False  # Opcional, para tornar o campo não obrigatório
    )
