# Generated by Django 5.2 on 2025-05-23 12:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0031_alter_classsession_start_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='classsession',
            name='range_radius',
            field=models.FloatField(default=10.0, help_text='Allowed distance in meters'),
        ),
    ]
