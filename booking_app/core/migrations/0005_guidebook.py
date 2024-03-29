# Generated by Django 4.0.10 on 2023-06-05 13:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_place'),
    ]

    operations = [
        migrations.CreateModel(
            name='Guidebook',
            fields=[
                ('rental_unit', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='core.rentalunit')),
                ('check_in_start_time', models.TimeField(blank=True)),
                ('check_in_end_time', models.TimeField(blank=True)),
                ('check_out_time', models.TimeField(blank=True)),
                ('check_in_method', models.CharField(choices=[], default="Someone will hand over the keys upon guest's arrival.", max_length=255)),
                ('check_in_instructions', models.TextField(blank=True)),
                ('house_manual', models.TextField(blank=True, default='Details such as wifi name and password.')),
                ('places_of_interest', models.ManyToManyField(blank=True, to='core.place')),
            ],
        ),
    ]
