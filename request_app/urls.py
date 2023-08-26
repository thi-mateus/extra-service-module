from django.urls import path
from . import views

app_name = 'request'

urlpatterns = [
    path('', views.Send.as_view(), name='send'),
    path('saverequest/', views.SaveRequest.as_view(), name='saverequest'),
    path('list/', views.List.as_view(), name='list'),
    path('detail/', views.Detail.as_view(), name='detail'),
]
