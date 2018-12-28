from django.shortcuts import render
from django.http import HttpResponse
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
        'new_game_1_pick': request.POST.get('game_1_pick', ''),
        'new_game_2_pick': request.POST.get('game_2_pick', ''),
        'new_game_3_pick': request.POST.get('game_3_pick', ''),
        'new_game_4_pick': request.POST.get('game_4_pick', ''),
    })
