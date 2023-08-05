from django.db import models
from django.contrib.auth.models import AbstractUser


class Military(AbstractUser):
    qra = models.CharField(max_length=100)
    grau_hierarquico = models.CharField()
    matricula = models.CharField(max_length=10, unique=True)
    telefone = models.CharField(max_length=20)
    email = models.EmailField()
    antiguidade = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.qra


class Scheduling(models.Model):
    militar = models.ForeignKey(Military, on_delete=models.PROTECT)
    qtd = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.qtd


class Permission(models.Model):
    militar = models.ForeignKey(Military, on_delete=models.PROTECT)
    id_permissao = models.CharField(
        max_length=5,
        default='USER',
        choices=(
            ('ADMIN', 'Administrador'),
            ('USER', 'Usuário'),
        )
    )

    def __str__(self):
        return self.qtd
