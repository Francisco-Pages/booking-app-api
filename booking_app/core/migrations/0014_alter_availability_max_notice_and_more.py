# Generated by Django 4.0.10 on 2023-06-01 15:16

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_availability'),
    ]

    operations = [
        migrations.AlterField(
            model_name='availability',
            name='max_notice',
            field=models.IntegerField(default=365, validators=[django.core.validators.MinValueValidator(31), django.core.validators.MaxValueValidator(365)]),
        ),
        migrations.AlterField(
            model_name='availability',
            name='max_stay',
            field=models.IntegerField(default=90, validators=[django.core.validators.MinValueValidator(8), django.core.validators.MaxValueValidator(90)]),
        ),
        migrations.AlterField(
            model_name='availability',
            name='min_notice',
            field=models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(30)]),
        ),
        migrations.AlterField(
            model_name='availability',
            name='min_stay',
            field=models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(7)]),
        ),
        migrations.AlterField(
            model_name='availability',
            name='prep_time',
            field=models.IntegerField(default=72, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(72)]),
        ),
    ]