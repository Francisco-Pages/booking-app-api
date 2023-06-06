# Generated by Django 4.0.10 on 2023-06-06 16:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_rename_places_of_interest_guidebook_places'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='guidebook',
            name='places',
        ),
        migrations.RemoveField(
            model_name='place',
            name='user',
        ),
        migrations.AddField(
            model_name='place',
            name='rental_unit',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.rentalunit'),
        ),
    ]
