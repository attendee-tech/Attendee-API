# Generated by Django 3.2.19 on 2025-04-23 20:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0019_alter_classsession_end_time_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classsession',
            name='start_time',
            field=models.TimeField(auto_now_add=True),
        ),
    ]
