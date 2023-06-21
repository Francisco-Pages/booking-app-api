# Generated by Django 4.0.10 on 2023-06-21 00:19

import core.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0034_rename_images_rentalunit_image_delete_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(null=True, upload_to=core.models.photo_file_path)),
                ('name', models.CharField(blank=True, max_length=255)),
                ('rental_unit', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.rentalunit')),
            ],
        ),
    ]
