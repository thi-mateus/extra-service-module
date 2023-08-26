from django.db import models
from profile_app.models import Military
from django.utils.text import slugify
from datetime import datetime
from PIL import Image
import os
from django.conf import settings


class Service(models.Model):
    local = models.CharField(max_length=50)
    hora_inicio = models.TimeField(default='08:00', verbose_name='Das')
    data_inicio = models.DateField(verbose_name='Do dia')
    hora_termino = models.TimeField(default='08:00', verbose_name='Às')
    data_termino = models.DateField(verbose_name='Ao dia')
    vagas = models.PositiveIntegerField()
    observacao = models.TextField(verbose_name='Observação')
    image = models.ImageField(
        upload_to='service_images/%Y/%m/', blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    militares = models.ManyToManyField(
        Military, related_name='servicos', blank=True)
    status = models.CharField(
        max_length=1,
        default='A',
        choices=(
            ('A', 'Aberto'),
            ('F', 'Fechado'),
        )
    )

    def __str__(self):
        return f'{self.local} - {self.data_inicio}'

    @staticmethod
    def resize_image(img, new_width=800):
        img_full_path = os.path.join(settings.MEDIA_ROOT, img.name)
        img_pil = Image.open(img_full_path)
        original_width, original_height = img_pil.size

        if original_width <= new_width:
            img_pil.close()
            return

        new_height = round((new_width * original_height) / original_width)

        new_img = img_pil.resize((new_width, new_height), Image.LANCZOS)
        new_img.save(
            img_full_path,
            optimize=True,
            quality=50
        )

    def save(self, *args, **kwargs):
        if not self.slug:
            slug = f'{slugify(self.local+"-"+str(self.data_inicio).replace("-", ""))}'
            self.slug = slug

        super().save(*args, **kwargs)

        if self.image:
            super().save(*args, **kwargs)

            max_image_size = 800

            if self.image:
                self.resize_image(self.image, max_image_size)
