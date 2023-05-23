# Generated by Django 4.0.10 on 2023-05-23 13:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_rename_amenities_amenitieslist_rentalunit_amenities'),
    ]

    operations = [
        migrations.CreateModel(
            name='DetailedLocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('neighborhood_description', models.TextField(default='Describe the neighborhood of your place.')),
                ('getting_around', models.TextField(default='Any tips about how to reach your place or interesting things around.')),
                ('location_sharing', models.BooleanField(default=False)),
                ('address1', models.CharField(blank=True, max_length=1024, verbose_name='Address line 1')),
                ('address2', models.CharField(blank=True, max_length=1024, verbose_name='Address line 2')),
                ('zip_code', models.CharField(blank=True, max_length=12, verbose_name='ZIP / Postal code')),
                ('city', models.CharField(blank=True, max_length=1024, verbose_name='City')),
                ('country', models.CharField(blank=True, max_length=3, verbose_name='Country')),
                ('longitude', models.DecimalField(decimal_places=6, default=0, max_digits=9)),
                ('latitude', models.DecimalField(decimal_places=6, default=0, max_digits=9)),
                ('location', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='detailed_location', to='core.rentalunit')),
            ],
        ),
        migrations.AddField(
            model_name='rentalunit',
            name='location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='core.detailedlocation'),
        ),
    ]
