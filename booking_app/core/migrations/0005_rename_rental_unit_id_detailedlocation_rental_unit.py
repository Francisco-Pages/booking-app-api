# Generated by Django 4.0.10 on 2023-05-26 14:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_detailedlocation'),
    ]

    operations = [
        migrations.RenameField(
            model_name='detailedlocation',
            old_name='rental_unit_id',
            new_name='rental_unit',
        ),
    ]
