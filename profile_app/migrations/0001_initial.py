# Generated by Django 4.2.4 on 2023-08-05 00:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Military',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('qra', models.CharField(max_length=100)),
                ('grau_hierarquico', models.CharField(max_length=20)),
                ('matricula', models.CharField(max_length=10, unique=True)),
                ('telefone', models.CharField(max_length=20)),
                ('email', models.EmailField(max_length=254)),
                ('antiguidade', models.PositiveSmallIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Scheduling',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('qtd', models.PositiveSmallIntegerField(default=0)),
                ('militar', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='profile_app.military')),
            ],
        ),
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_permissao', models.CharField(choices=[('ADMIN', 'Administrador'), ('USER', 'Usuário')], default='USER', max_length=5)),
                ('militar', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='profile_app.military')),
            ],
        ),
    ]
