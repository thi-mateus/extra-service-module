from django.contrib import admin
from . import models
from utils import utils


class ServiceAdmin(admin.ModelAdmin):

    # Método personalizado para exibir militares na lista de exibição
    @admin.display(description='Militares')
    def exibir_militares(self, obj):
        return ", ".join([militar.grau_hierarquico+" "+militar.qra for militar in obj.militares.all()])

    @admin.display(description='Das')
    def get_hora_inicio_formatada(self, obj):
        return utils.format_time_service(obj.hora_inicio)

    @admin.display(description='Às')
    def get_hora_termino_formatada(self, obj):
        return utils.format_time_service(obj.hora_termino)

    @admin.display(description='Do dia')
    def get_data_inicio_formatado(self, obj):
        return utils.format_date(obj.data_inicio)

    @admin.display(description='Ao dia')
    def get_data_termino_formatado(self, obj):
        return utils.format_date(obj.data_termino)

    list_display = ['local', 'get_data_inicio_formatado', 'get_hora_inicio_formatada', 'get_data_termino_formatado',
                    'get_hora_termino_formatada', 'vagas', 'observacao', 'exibir_militares']


admin.site.register(models.Service, ServiceAdmin)
