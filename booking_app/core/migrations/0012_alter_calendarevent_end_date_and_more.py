# Generated by Django 4.0.10 on 2023-06-09 15:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_reservation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='calendarevent',
            name='end_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='calendarevent',
            name='start_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
