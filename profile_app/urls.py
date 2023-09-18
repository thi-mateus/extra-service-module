from django.urls import path
from . import views

app_name = 'profile'

urlpatterns = [
    path('', views.Create.as_view(), name='create'),
    path('list_requests/<int:pk>',
         views.ListRequests.as_view(), name='list_requests'),
    path('update/', views.Update.as_view(), name='update'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('listar_militares/', views.ListarMilitares.as_view(),
         name='listar_militares'),
    path('gerar_pdf_militares/', views.GerarPDFMilitares.as_view(),
         name='gerar_pdf_militares'),
    path('gerar_pdf/', views.GerarPDF.as_view(),
         name='gerar_pdf'),
]
