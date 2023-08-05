from django.db import models
from profile_app.models import Military


class Service(models.Model):
    local = models.CharField(max_length=50)
    hora_inicio = models.TimeField(default='08:00')
    data_inicio = models.DateField()
    hora_termino = models.TimeField(default='08:00')
    data_termino = models.DateField()
    vagas = models.PositiveIntegerField()
    observacao = models.TextField()
    militar = models.ManyToManyField(Military)

    def __str__(self):
        return self.local