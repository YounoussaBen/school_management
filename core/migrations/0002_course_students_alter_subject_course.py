# Generated by Django 5.1 on 2024-08-23 10:34

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='students',
            field=models.ManyToManyField(limit_choices_to={'role': 'Student'}, related_name='courses', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='subject',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subjects', to='core.course'),
        ),
    ]
