# Generated by Django 4.2.4 on 2023-08-05 00:38

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('profile_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('local', models.CharField(max_length=50)),
                ('hora_inicio', models.TimeField(default='08:00')),
                ('data_inicio', models.DateField()),
                ('hora_termino', models.TimeField(default='08:00')),
                ('data_termino', models.DateField()),
                ('vagas', models.PositiveIntegerField()),
                ('observacao', models.TextField()),
                ('militar', models.ManyToManyField(related_name='militar_servico', to='profile_app.military')),
            ],
        ),
    ]
