from django.contrib import admin
from . import models

admin.site.register(models.Delito)
admin.site.register(models.Ocorrencia)
admin.site.register(models.Recompensa)
