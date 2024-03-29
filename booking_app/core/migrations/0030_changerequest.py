# Generated by Django 4.0.10 on 2023-06-18 22:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0029_reservation_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChangeRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('new_check_in', models.DateField()),
                ('new_check_out', models.DateField()),
                ('status', models.BooleanField(default=False)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('nights_diff', models.IntegerField(null=True)),
                ('reservation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.reservation')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
