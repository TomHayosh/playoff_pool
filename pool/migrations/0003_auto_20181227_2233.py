# Generated by Django 2.1.1 on 2018-12-27 22:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pool', '0002_auto_20181227_2133'),
    ]

    operations = [
        migrations.AddField(
            model_name='pickset',
            name='round_1_game_1',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='pickset',
            name='round_1_game_2',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='pickset',
            name='round_1_game_3',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='pickset',
            name='round_1_game_4',
            field=models.IntegerField(default=0),
        ),
    ]
