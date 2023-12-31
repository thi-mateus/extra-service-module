from django.db import models
from profile_app.models import Military
from service_app.models import Service
from rodadas.models import Rodada


class Request(models.Model):
    id_mil = models.ForeignKey(Military, on_delete=models.CASCADE)
    id_sv = models.ForeignKey(Service, on_delete=models.CASCADE)
    id_rod = models.ForeignKey(Rodada, on_delete=models.CASCADE)
    id_opcao = models.PositiveSmallIntegerField()
    data_solicitacao = models.DateTimeField()
    status = models.CharField(
        max_length=1,
        default='S',
        choices=(
            ('S', 'Solicitado'),
            ('A', 'Agendado'),
            ('N', 'Negado'),
        )
    )
    criterio = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.id_mil} - {self.id_sv} - {self.id_opcao}ª opção"

    class Meta:
        unique_together = ('id_mil', 'id_sv')
