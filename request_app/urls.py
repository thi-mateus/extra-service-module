from django.urls import path
from . import views

app_name = 'request'

urlpatterns = [
    path('', views.Pay.as_view(), name='pay'),
    path('finalizerequest/', views.FinalizeRequest.as_view(), name='finalizerequest'),
    path('detail/', views.Detail.as_view(), name='detail'),
]
