# Generated by Django 3.2.19 on 2025-04-25 05:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0022_alter_classsession_start_time'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='classsession',
            name='end_time',
        ),
        migrations.RemoveField(
            model_name='classsession',
            name='start_time',
        ),
        migrations.AddField(
            model_name='classsession',
            name='duration_time',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
