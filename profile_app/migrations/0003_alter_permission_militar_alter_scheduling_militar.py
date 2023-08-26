# Generated by Django 4.2.3 on 2023-08-06 15:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('profile_app', '0002_military_usuario'),
    ]

    operations = [
        migrations.AlterField(
            model_name='permission',
            name='militar',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='profile_app.military'),
        ),
        migrations.AlterField(
            model_name='scheduling',
            name='militar',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='profile_app.military'),
        ),
    ]