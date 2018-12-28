from django.shortcuts import render, redirect
from pool.models import PickSet


# Create your views here.
def home_page(request):
    return render(request, 'home.html')


def view_picks(request, pick_set_id):
    template_to_use = 'picks.html'
    pick_set = PickSet.objects.first()
    if pick_set is None:
        return render(request, template_to_use)
    return render(request, template_to_use, {
        'new_game_1_pick': pick_set.round_1_game_1,
        'new_game_2_pick': pick_set.round_1_game_2,
        'new_game_3_pick': pick_set.round_1_game_3,
        'new_game_4_pick': pick_set.round_1_game_4,
    })


def new_picks(request):
    # Selecting by [0] here gives the first char of '24' from ('24',)
    temp_round_1_game_1 = request.POST['game_1_pick'],
    temp_round_1_game_2 = request.POST['game_2_pick'],
    temp_round_1_game_3 = request.POST['game_3_pick'],
    temp_round_1_game_4 = request.POST['game_4_pick'],
    pick_set = PickSet.objects.create(
        # Selecting by [0] here gives the integer 24. Weird.
        round_1_game_1=temp_round_1_game_1[0],
        round_1_game_2=temp_round_1_game_2[0],
        round_1_game_3=temp_round_1_game_3[0],
        round_1_game_4=temp_round_1_game_4[0],
    )
    return redirect(f'/picks/{pick_set.id}/')
