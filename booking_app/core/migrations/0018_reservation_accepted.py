# Generated by Django 4.0.10 on 2023-06-12 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_calendarevent_night_subtotal'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='accepted',
            field=models.BooleanField(default=False),
        ),
    ]