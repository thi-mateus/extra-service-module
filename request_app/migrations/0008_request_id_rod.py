# Generated by Django 4.2.4 on 2023-09-26 11:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rodadas', '0007_alter_rodada_data_fim'),
        ('request_app', '0007_alter_request_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='request',
            name='id_rod',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='rodadas.rodada'),
            preserve_default=False,
        ),
    ]
