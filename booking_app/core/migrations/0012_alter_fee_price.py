# Generated by Django 4.0.10 on 2023-05-30 16:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_fee'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fee',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=8, null=True),
        ),
    ]