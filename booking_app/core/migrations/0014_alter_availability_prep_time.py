# Generated by Django 4.0.10 on 2023-06-09 20:35

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_reservation_creation_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='availability',
            name='prep_time',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)]),
        ),
    ]
