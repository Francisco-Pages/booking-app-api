# Generated by Django 4.0.10 on 2023-06-14 13:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_reservation_accepted'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Reservation',
        ),
    ]
