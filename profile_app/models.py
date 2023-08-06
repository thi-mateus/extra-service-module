from django.db import models
from django.contrib.auth.models import User


# Classe Militares


class Military(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE,
                                   verbose_name='Usuário')
    qra = models.CharField(max_length=100)
    grau_hierarquico = models.CharField(max_length=20)
    matricula = models.CharField(max_length=10, unique=True)
    telefone = models.CharField(max_length=20)
    email = models.EmailField()
    antiguidade = models.PositiveSmallIntegerField()

    def __str__(self):
        return f"{self.grau_hierarquico} {self.qra} - {self.matricula}"


# Classe de agendamentos realizados pelos militares
class Scheduling(models.Model):
    militar = models.ForeignKey(Military, on_delete=models.CASCADE)
    qtd = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return f"{Military.__str__(self.militar)} : {self.qtd}"


# Classe de permissões dos militares
class Permission(models.Model):
    militar = models.ForeignKey(Military, on_delete=models.CASCADE)
    id_permissao = models.CharField(
        max_length=5,
        default='USER',
        choices=(
            ('ADMIN', 'Administrador'),
            ('USER', 'Usuário'),
        )
    )

    def __str__(self):
        return f"{Military.__str__(self.militar)} : {self.id_permissao}"
