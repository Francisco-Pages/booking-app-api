# Generated by Django 4.0.10 on 2023-06-20 18:25

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0031_remove_changerequest_nights_diff'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rentalunit',
            name='images',
            field=models.ImageField(null=True, upload_to=core.models.rental_unit_image_file_path),
        ),
    ]
