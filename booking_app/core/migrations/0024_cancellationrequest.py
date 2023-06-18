# Generated by Django 4.0.10 on 2023-06-16 19:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0023_reservation_reservation_request'),
    ]

    operations = [
        migrations.CreateModel(
            name='CancellationRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.BooleanField(default=False)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('reason', models.TextField(blank=True)),
                ('refund', models.DecimalField(decimal_places=2, max_digits=8, null=True)),
                ('reservation', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.reservation')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]