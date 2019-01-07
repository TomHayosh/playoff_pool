from django.db import models


# Create your models here.
class PickSet(models.Model):
    name = models.TextField(default='')
    results_preference = models.IntegerField(default=0)
    round_1_game_1_team = models.IntegerField(default=1)
    round_1_game_1 = models.IntegerField(default=-0)
    round_1_game_2_team = models.IntegerField(default=1)
    round_1_game_2 = models.IntegerField(default=-0)
    round_1_game_3_team = models.IntegerField(default=1)
    round_1_game_3 = models.IntegerField(default=-0)
    round_1_game_4_team = models.IntegerField(default=1)
    round_1_game_4 = models.IntegerField(default=-0)
    wc_game_1_team = models.IntegerField(default=1)
    wc_game_1 = models.IntegerField(default=-0)
    wc_game_2_team = models.IntegerField(default=1)
    wc_game_2 = models.IntegerField(default=-0)
    wc_game_3_team = models.IntegerField(default=1)
    wc_game_3 = models.IntegerField(default=-0)
    wc_game_4_team = models.IntegerField(default=1)
    wc_game_4 = models.IntegerField(default=-0)
