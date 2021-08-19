# Generated by Django 3.1.5 on 2021-08-15 10:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0009_sentiment_vote'),
    ]

    operations = [
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.TextField(max_length=40)),
                ('last_name', models.TextField(max_length=40)),
                ('middle_name', models.TextField(max_length=40)),
                ('address', models.TextField(max_length=100)),
                ('covid_grade', models.CharField(choices=[('1', 'low'), ('2', 'middle'), ('3', 'high')], max_length=1)),
                ('lung_damage', models.FloatField(default=0.0, verbose_name='percentage of lung damage')),
                ('last_temperature', models.FloatField(default=0.0, verbose_name='body temperature')),
                ('shortness_of_breath', models.BooleanField(default=False, verbose_name='shortness of breath')),
                ('last_heart_rate', models.IntegerField(default=-1, verbose_name='Heart rate per minute')),
                ('last_saturation', models.IntegerField(default=-1, verbose_name='saturation')),
                ('chest_tightness', models.BooleanField(default=False, verbose_name='chest_tightness')),
                ('vomiting', models.BooleanField(default=False, verbose_name='vomiting')),
                ('dizziness', models.BooleanField(default=False, verbose_name='dizziness')),
                ('headache', models.BooleanField(default=False, verbose_name='headache')),
                ('blurred_consciousness', models.BooleanField(default=False, verbose_name='blurred_consciousness')),
                ('sweating', models.BooleanField(default=False, verbose_name='sweating')),
                ('violation_of_balance_and_coordination', models.BooleanField(default=False, verbose_name='violation_of_balance_and_coordination')),
                ('need_oxygen_support', models.BooleanField(default=False, verbose_name='need_oxygen_support')),
            ],
        ),
    ]
