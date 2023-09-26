from django.db import models
from django.utils import timezone
from datetime import timedelta

from service_app.models import Service

# Lista de opções para mes_referencia
MESES_CHOICES = [
    (1, 'Janeiro'),
    (2, 'Fevereiro'),
    (3, 'Março'),
    (4, 'Abril'),
    (5, 'Maio'),
    (6, 'Junho'),
    (7, 'Julho'),
    (8, 'Agosto'),
    (9, 'Setembro'),
    (10, 'Outubro'),
    (11, 'Novembro'),
    (12, 'Dezembro'),
]


class Rodada(models.Model):
    data_inicio = models.DateTimeField(default=timezone.now)
    data_fim = models.DateTimeField(
        default=timezone.now() + timedelta(days=1))
    status = models.CharField(
        max_length=1,
        default='A',
        choices=(
            ('A', 'Aberta'),
            ('F', 'Fechada'),
        )
    )
    numero = models.PositiveIntegerField(default=0)
    ano_referencia = models.IntegerField(
        default=timezone.now().year,
    )
    mes_referencia = models.PositiveSmallIntegerField(
        default=timezone.now().month, choices=MESES_CHOICES)

    services = models.ManyToManyField(
        Service, related_name='rodadas', blank=True)

    def __str__(self):
        return f'Rodada {self.id}'

    def save(self, *args, **kwargs):

        if not self.ano_referencia:
            self.ano_referencia = timezone.now().year

        if self.ano_referencia and self.mes_referencia:
            # Verifica se já existem rodadas com o mesmo ano e mês de referência
            rodadas_no_mes = Rodada.objects.filter(
                ano_referencia=self.ano_referencia,
                mes_referencia=self.mes_referencia
            )

            if rodadas_no_mes.exists():
                # Se existem rodadas no mesmo mês, obtemos o número máximo e incrementamos
                # Essa abordagem garante que a numeração seja única e não tenha lacunas, mesmo após exclusões no banco de dados
                self.numero = rodadas_no_mes.aggregate(models.Max('numero'))[
                    'numero__max'] + 1
            else:
                # Se não existem rodadas no mesmo mês, começamos com 1
                self.numero = 1

        super().save(*args, **kwargs)

    def clean(self):
        if self.ano_referencia < 2023 or self.ano_referencia > (timezone.now().year + 1):
            # 2023 foi o ano de criação do sistema
            raise ValidationError(
                "Ano de referência fora do intervalo permitido.")
