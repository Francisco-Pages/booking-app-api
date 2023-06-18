# Generated by Django 4.0.10 on 2023-06-17 18:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0026_rename_days_reservation_nights'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rulebook',
            name='cancellation_policy',
            field=models.CharField(choices=[('Flexible', 'flexible'), ('Moderate', 'moderate'), ('Firm', 'firm'), ('Strict', 'strict'), ('Firm Long Term', 'firm long Term'), ('Strict Long Term', 'strict long Term'), ('Super Strict 30', 'super strict 30'), ('Non-refundable', 'non-refundable')], default='Flexible', max_length=50),
        ),
    ]