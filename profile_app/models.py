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

    class Meta:
        verbose_name = 'Militar'
        verbose_name_plural = 'Militares'


class BaseBanco(models.Model):
    militar = models.OneToOneField(
        Military, on_delete=models.CASCADE)

    class Meta:
        abstract = True

    def somar(self, valor):
        if valor < 0:
            raise ValueError("O valor a ser somado deve ser positivo.")
        self._realizar_soma(valor)

    def _realizar_soma(self, valor):
        raise NotImplementedError(
            "A subclasse deve implementar este método.")


class BancoDePontos(BaseBanco):
    pontos = models.PositiveIntegerField(default=0)

    def _realizar_soma(self, valor):
        self.pontos += valor
        self.save()

    def __str__(self):
        return f"{self.militar.grau_hierarquico} {self.militar.qra} ({self.militar.matricula}): {self.pontos} pts"

    class Meta:
        verbose_name = 'Banco de Pontos'
        verbose_name_plural = 'Bancos de Pontos'


class BancoDeHoras(BaseBanco):
    horas = models.PositiveIntegerField(default=0)

    def _realizar_soma(self, valor):
        self.horas += valor
        self.save()

    def __str__(self):
        return f"{self.militar.grau_hierarquico} {self.militar.qra} ({self.militar.matricula}): {self.horas} h"

    class Meta:
        verbose_name = 'Banco de Horas'
        verbose_name_plural = 'Bancos de Horas'


# Classe de agendamentos realizados pelos militares
class Scheduling(models.Model):
    militar = models.ForeignKey(
        Military, on_delete=models.CASCADE)
    qtd = models.PositiveSmallIntegerField(default=0)
    mes_referencia = models.DateField()

    def __str__(self):
        return f"{Military.__str__(self.militar)} : {self.qtd} ({self.mes_referencia.strftime('%B %Y')})"

    class Meta:
        verbose_name = 'Agendamento'
        verbose_name_plural = 'Agendamentos'


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

    class Meta:
        verbose_name = 'Permissão'
        verbose_name_plural = 'Permissões'
