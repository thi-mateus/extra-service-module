from django.urls import path
from . import views

app_name = 'ocorrencia'

urlpatterns = [
    path('criar_ocorrencia/',
         views.Criar.as_view(), name='criar_ocorrencia'),

]
