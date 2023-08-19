from django.urls import path
from . import views

app_name = 'request'

urlpatterns = [
    path('', views.Pay.as_view(), name='pay'),
    path('saverequest/', views.SaveRequest.as_view(), name='saverequest'),
    path('detail/', views.Detail.as_view(), name='detail'),
]
