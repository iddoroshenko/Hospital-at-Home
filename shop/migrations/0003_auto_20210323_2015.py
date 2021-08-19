# Generated by Django 3.1.5 on 2021-03-23 20:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0002_review_author'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='rating',
            field=models.CharField(choices=[('1', 'terrible'), ('2', 'bad'), ('3', 'average'), ('4', 'good'), ('5', 'perfect')], max_length=1),
        ),
    ]