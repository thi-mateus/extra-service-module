from django.contrib import admin
from . import models

admin.site.register(models.Military)
admin.site.register(models.Scheduling)
admin.site.register(models.Permission)
admin.site.register(models.BancoDeHoras)
admin.site.register(models.BancoDePontos)
