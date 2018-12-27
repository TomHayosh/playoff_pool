from django.db import models


# Create your models here.
class PickSet(models.Model):
    round_1_game_1 = models.IntegerField(default=-0)
    round_1_game_2 = models.IntegerField(default=-0)
    round_1_game_3 = models.IntegerField(default=-0)
    round_1_game_4 = models.IntegerField(default=-0)
