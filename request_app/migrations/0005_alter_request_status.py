# Generated by Django 4.2.4 on 2023-09-07 16:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('request_app', '0004_alter_request_data_solicitacao'),
    ]

    operations = [
        migrations.AlterField(
            model_name='request',
            name='status',
            field=models.CharField(choices=[('S', 'Solicitado'), ('A', 'Agendado'), ('N', 'Negado')], default='S', max_length=1),
        ),
    ]
