# Generated by Django 3.2.19 on 2025-04-12 09:11

import base.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0011_auto_20250412_0910'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='matricule_number',
            field=models.CharField(max_length=13, unique=True, validators=[base.models.student_matricule_validator]),
        ),
    ]
