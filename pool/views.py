from django.shortcuts import render
from pool.models import PickSet


# Create your views here.
def home_page(request):
    pick_set = PickSet()
    pick_set.round_1_game_1 = request.POST.get('game_1_pick', 0)
    pick_set.round_1_game_2 = request.POST.get('game_2_pick', 0)
    pick_set.round_1_game_3 = request.POST.get('game_3_pick', 0)
    pick_set.round_1_game_4 = request.POST.get('game_4_pick', 0)
    pick_set.save()

    return render(request, 'home.html', {
        'new_game_1_pick': pick_set.round_1_game_1,
        'new_game_2_pick': pick_set.round_1_game_2,
        'new_game_3_pick': pick_set.round_1_game_3,
        'new_game_4_pick': pick_set.round_1_game_4,
    })
