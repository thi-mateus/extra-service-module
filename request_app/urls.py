from django.urls import path
from . import views

app_name = 'request'

urlpatterns = [
    path('list_requests/',
         views.ListRequests.as_view(), name='list_requests'),
    path('saverequest/', views.SaveRequest.as_view(), name='saverequest'),
    path('select/', views.Select.as_view(), name='select'),
    path('detail/', views.Detail.as_view(), name='detail'),
]
