# Generated by Django 4.2.4 on 2023-09-26 10:12

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rodadas', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rodada',
            name='data_fim',
            field=models.DateTimeField(default=datetime.datetime(2023, 9, 27, 10, 12, 19, 575430, tzinfo=datetime.timezone.utc)),
        ),
    ]