# Generated by Django 5.1 on 2024-08-25 12:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_subject_credits'),
    ]

    operations = [
        migrations.AddField(
            model_name='grade',
            name='remarks',
            field=models.TextField(blank=True, null=True),
        ),
    ]
