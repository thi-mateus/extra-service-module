from django.db import models

from profile_app.models import Military


class Delito(models.Model):
    nome = models.CharField(max_length=200)

    def __str__(self):
        return {self.nome}

    class Meta:
        verbose_name = 'Delito'
        verbose_name_plural = 'Delitos'


class Ocorrencia(models.Model):
    data = models.DateField()
    local = models.CharField(max_length=100)
    delitos = models.ManyToManyField(
        Delito, related_name='situacoes')
    militares = models.ManyToManyField(
        Military, related_name='ocorrencias')
    documento = models.FileField(upload_to='sistema_de_pontos/%Y/%m/')

    def __str__(self):
        delitos_relacionados = self.delitos.all()
        nomes_delitos = [delito.nome for delito in delitos_relacionados]
        return f'Ocorrência em {self.data} com os delitos: {", ".join(nomes_delitos)}'

    class Meta:
        verbose_name = 'Ocorrência'
        verbose_name_plural = 'Ocorrências'


class Recompensa(models.Model):
    delito = models.ForeignKey(Delito, on_delete=models.CASCADE)
    equivalente_horas = models.SmallIntegerField(
        verbose_name='equivalente em horas')
    equivalente_pontos = models.SmallIntegerField(
        verbose_name='equivalente em pontos')

    def __str__(self):
        return f'{self.delito}: {equivalente_horas} horas, {equivalente_horas} pontos'

    class Meta:
        verbose_name = 'Recompensa'
        verbose_name_plural = 'Recompensas'
