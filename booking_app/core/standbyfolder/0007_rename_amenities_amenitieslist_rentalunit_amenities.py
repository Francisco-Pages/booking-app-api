# Generated by Django 4.0.10 on 2023-05-23 13:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_remove_rentalunit_house_rules_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Amenities',
            new_name='AmenitiesList',
        ),
        migrations.AddField(
            model_name='rentalunit',
            name='amenities',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='core.amenitieslist'),
        ),
    ]
