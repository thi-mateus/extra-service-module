# Generated by Django 4.2.4 on 2023-08-26 00:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('request_app', '0003_rename_requests_request'),
    ]

    operations = [
        migrations.AlterField(
            model_name='request',
            name='data_solicitacao',
            field=models.DateTimeField(),
        ),
    ]
