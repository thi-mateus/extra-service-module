from django.urls import path
from . import views

app_name = 'request'

urlpatterns = [
    path('list_requests/',
         views.ListRequests.as_view(), name='list_requests'),
    path('saverequest/', views.SaveRequest.as_view(), name='saverequest'),
    path('classificacao_por_criterios/<int:listar_todos>/',
         views.ClassificacaoPorCriterios.as_view(), name='classificacao_por_criterios'),
    path('selecionados/', views.SelecionarMilitares.as_view(),
         name='selecionados'),
    path('detail/', views.Detail.as_view(), name='detail'),
]
