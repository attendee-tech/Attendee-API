# Generated by Django 3.2.19 on 2025-04-25 16:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0026_alter_user_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendance',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.user'),
        ),
        migrations.AlterField(
            model_name='classsession',
            name='lecturer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.user'),
        ),
    ]
