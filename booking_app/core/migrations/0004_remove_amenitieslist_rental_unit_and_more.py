# Generated by Django 4.0.10 on 2023-05-23 20:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_rentalunit_max_guests'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='amenitieslist',
            name='rental_unit',
        ),
        migrations.RemoveField(
            model_name='detailedlocation',
            name='rental_unit',
        ),
        migrations.AddField(
            model_name='rentalunit',
            name='amenities',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='core.amenitieslist'),
        ),
        migrations.AddField(
            model_name='rentalunit',
            name='location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='core.detailedlocation'),
        ),
    ]
