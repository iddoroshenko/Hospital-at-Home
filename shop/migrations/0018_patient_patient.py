# Generated by Django 3.1.5 on 2021-08-19 19:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('shop', '0017_patient_birth'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='patient',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='user_patient', to=settings.AUTH_USER_MODEL),
        ),
    ]
