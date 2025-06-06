# Generated by Django 3.2.19 on 2025-04-25 12:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0023_auto_20250425_0517'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]
