# Generated by Django 4.0.10 on 2023-06-05 16:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_alter_place_address1_alter_place_address2_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='guidebook',
            old_name='places_of_interest',
            new_name='places',
        ),
    ]