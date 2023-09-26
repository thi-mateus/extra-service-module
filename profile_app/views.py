from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.views import View
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import copy
from datetime import datetime

from reportlab.pdfgen import canvas
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.conf import settings
import os

from django.http import FileResponse
from django.shortcuts import render
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

from openpyxl import Workbook


from .models import Military, Scheduling
from . import forms


class ListRequests(DetailView):
    template_name = 'profile/list_requests.html'
    model = Military
    pk_url_kwarg = 'pk'
    context_object_name = 'military'


class BaseProfile(View):
    template_name = 'profile/create.html'

    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)

        self.cart = copy.deepcopy(self.request.session.get('cart', {}))

        self.profile = None

        if self.request.user.is_authenticated:
            self.profile = Military.objects.filter(
                usuario=self.request.user).first()

            self.context = {
                'userform': forms.UserForm(
                    data=self.request.POST or None,
                    usuario=self.request.user,
                    instance=self.request.user,
                ),
                'perfilform': forms.PerfilForm(
                    data=self.request.POST or None,
                    instance=self.profile

                )
            }
        else:
            self.context = {
                'userform': forms.UserForm(data=self.request.POST or None),
                'perfilform': forms.PerfilForm(data=self.request.POST or None)
            }

        self.userform = self.context['userform']
        self.perfilform = self.context['perfilform']

        if self.request.user.is_authenticated:
            self.template_name = 'profile/update.html'

        self.renderizar = render(
            self.request, self.template_name, self.context)

    def get(self, *args, **kwargs):
        return self.renderizar


class Create(BaseProfile):
    def post(self, *args, **kwargs):
        if not self.userform.is_valid() or not self.perfilform.is_valid():
            messages.error(
                self.request,
                'Existem erros no formulário de cadastro. Verifique se todos '
                'os dados forma preenchidos corretamente.'
            )
            return self.renderizar

        username = self.userform.cleaned_data.get('username')
        password = self.userform.cleaned_data.get('password')
        email = self.userform.cleaned_data.get('email')
        first_name = self.userform.cleaned_data.get('first_name')
        last_name = self.userform.cleaned_data.get('last_name')

        # Usuário logado
        if self.request.user.is_authenticated:
            usuario = get_object_or_404(
                User, username=self.request.user.username)
            usuario.username = username

            if password:
                usuario.set_password(password)

            usuario.email = email
            usuario.first_name = first_name
            usuario.last_name = last_name
            usuario.save()

            if not self.profile:
                self.perfilform.cleaned_data['usuario'] = usuario
                profile = Military(**self.perfilform.cleaned_data)
                profile.save()
            else:
                profile = self.perfilform.save(commit=False)
                profile.usuario = usuario
                profile.save()

        # Usuário NÃO logado (novo)
        else:
            usuario = self.userform.save(commit=False)
            usuario.set_password(password)
            usuario.save()

            profile = self.perfilform.save(commit=False)
            profile.usuario = usuario
            profile.save()

            # Criar a instância de Agendamento
            scheduling = Scheduling(
                militar=profile, mes_referencia=datetime.today())
            scheduling.save()

            if password:
                auth = authenticate(
                    self.request,
                    username=usuario,
                    password=password
                )

                if auth:
                    login(self.request, user=usuario)

        self.request.session['cart'] = self.cart
        self.request.session.save()

        messages.success(
            self.request,
            'Seu cadastro foi criado ou atualizado com sucesso.'
        )

        messages.success(
            self.request,
            'Você fez login e pode concluir sua solicitação.'
        )

        return redirect('profile:create')
        return self.renderizar


class Update(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Update')


class Login(View):
    def post(self, *args, **kwargs):
        username = self.request.POST.get('username')
        password = self.request.POST.get('password')

        if not username or not password:
            messages.error(
                self.request,
                'Usuário ou senha inválidos!'
            )
            return redirect('profile:create')

        usuario = authenticate(
            self.request, username=username, password=password)

        if not usuario:
            messages.error(
                self.request,
                'Usuário ou senha inválidos!'
            )
            return redirect('profile:create')

        login(self.request, user=usuario)
        messages.success(
            self.request,
            'Você fez login e pode concluir sua solicitação.'
        )
        return redirect('service:cart')


class Logout(View):
    def get(self, *args, **kwargs):
        cart = copy.deepcopy(self.request.session.get('cart'))
        logout(self.request)
        self.request.session['cart'] = cart
        self.request.session.save()
        return redirect('service:list')


class ListarMilitares(ListView):
    model = Military
    template_name = 'profile/listar_militares.html'
    context_object_name = 'militares'
    paginate_by = 25

    def get_queryset(self):
        order_by = self.request.GET.get('order_by')
        direction = self.request.GET.get(
            'direction', 'asc')  # Padrão para ascendente

        if order_by:
            if direction == 'desc':
                # Adiciona '-' para ordenação descendente
                order_by = f'-{order_by}'

            queryset = Military.objects.all().order_by(order_by)
        else:
            queryset = Military.objects.all().order_by('antiguidade')  # Ordenação padrão

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_by'] = self.request.GET.get('order_by')
        context['direction'] = self.request.GET.get('direction', 'asc')

        # Verifica e ajusta a direção para alternar entre 'asc' e 'desc'
        if context['direction'] == 'asc':
            context['toggle_direction'] = 'desc'
        else:
            context['toggle_direction'] = 'asc'

        # Adicione a variável 'columns' ao contexto aqui
        context['columns'] = [
            {'name': 'qra', 'display_name': 'Militar'},
            {'name': 'grau_hierarquico', 'display_name': 'Grau Hierárquico'},
            {'name': 'matricula', 'display_name': 'Matrícula'},
            {'name': 'antiguidade', 'display_name': 'Antiguidade'},
            {'name': 'email', 'display_name': 'Email'},
            {'name': 'telefone', 'display_name': 'Telefone'},

        ]

        return context


class GerarPDFMilitares(View):

    @staticmethod
    def link_callback(uri, rel):
        # Simplesmente retorna uma string vazia para evitar erros de link
        return ''

    def get(self, request):
        militares = Military.objects.all()  # Recupere os dados do modelo de Militares

        # Defina a variável 'columns' com as informações das colunas
        columns = [
            {'name': 'qra', 'display_name': 'Militar'},
            {'name': 'grau_hierarquico', 'display_name': 'Grau Hierárquico'},
            {'name': 'matricula', 'display_name': 'Matrícula'},
            # Adicione as informações das outras colunas aqui
        ]

        # Renderize o template HTML com os dados e as colunas
        template = get_template('profile/listar_militares.html')
        context = {'militares': militares, 'columns': columns}
        html = template.render(context)

        # Crie um arquivo PDF a partir do HTML
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="relacao_militares_ft.pdf"'

        pisa_status = pisa.CreatePDF(
            html, dest=response, link_callback=self.link_callback)

        if pisa_status.err:
            return HttpResponse('Ocorreu um erro ao gerar o PDF.')

        return response


class GerarPDF(View):
    def get(self, request):
        # Crie um objeto BytesIO para armazenar o PDF
        buffer = BytesIO()

        # Recupere os dados dos militares (você pode ajustar a consulta conforme necessário)
        militares = Military.objects.all()

        # Crie um documento PDF com o ReportLab
        doc = SimpleDocTemplate(buffer, pagesize=letter)

        # Crie uma lista para armazenar o conteúdo do PDF
        elements = []

        # Defina o título personalizado
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="relacao_militares_ft.pdf"'
        response['Content-Title'] = 'Relação dos Militares da Força Tática'

        # Crie um estilo para o título
        styles = getSampleStyleSheet()
        title_style = styles['Title']

        # Adicione um título ao PDF como um objeto Paragraph com o estilo personalizado
        title = Paragraph("Relação dos Militares da Força Tática", title_style)
        elements.append(title)

        # Restante do código para a tabela
        # Crie uma tabela para exibir os dados dos militares
        data = [['Nome', 'Grau Hierárquico', 'Matrícula']]
        for militar in militares:
            data.append(
                [militar.qra, militar.grau_hierarquico, militar.matricula])

        # Configure a tabela
        table = Table(data)
        table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                   ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                   ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                   ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                   ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                   ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                                   ('GRID', (0, 0), (-1, -1), 1, colors.black)]))

        # Adicione a tabela ao documento PDF
        elements.append(table)

        # Construa o PDF
        doc.build(elements)

        # Configure a resposta HTTP com o conteúdo do BytesIO
        buffer.seek(0)
        response.write(buffer.read())

        return response
