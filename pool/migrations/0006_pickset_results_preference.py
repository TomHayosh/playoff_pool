# Generated by Django 2.1.2 on 2019-01-04 21:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pool', '0005_added_fields_for_home_or_away_team'),
    ]

    operations = [
        migrations.AddField(
            model_name='pickset',
            name='results_preference',
            field=models.IntegerField(default=0),
        ),
    ]
