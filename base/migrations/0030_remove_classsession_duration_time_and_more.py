# Generated by Django 5.2 on 2025-05-20 19:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0029_alter_classsession_lecturer'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='classsession',
            name='duration_time',
        ),
        migrations.RemoveField(
            model_name='classsession',
            name='level',
        ),
        migrations.AddField(
            model_name='classsession',
            name='end_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='classsession',
            name='hall',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='classsession',
            name='start_time',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='class_session',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendances', to='base.classsession'),
        ),
        migrations.AlterField(
            model_name='classsession',
            name='latitude',
            field=models.FloatField(default=1.0),
        ),
        migrations.AlterField(
            model_name='classsession',
            name='longitude',
            field=models.FloatField(default=1.0),
        ),
    ]
