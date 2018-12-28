from django.shortcuts import render
from pool.models import PickSet


# Create your views here.
def home_page(request):
    new_round_1_game_1 = 0
    new_round_1_game_2 = 0
    new_round_1_game_3 = 0
    new_round_1_game_4 = 0

    if request.method == 'POST':
        # Selecting by [0] here gives the first char of '24' from ('24',)
        temp_round_1_game_1 = request.POST['game_1_pick'],
        temp_round_1_game_2 = request.POST['game_2_pick'],
        temp_round_1_game_3 = request.POST['game_3_pick'],
        temp_round_1_game_4 = request.POST['game_4_pick'],
        PickSet.objects.create(
            # Selecting by [0] here gives the integer 24. Weird.
            round_1_game_1=temp_round_1_game_1[0],
            round_1_game_2=temp_round_1_game_2[0],
            round_1_game_3=temp_round_1_game_3[0],
            round_1_game_4=temp_round_1_game_4[0],
        )
        new_round_1_game_1 = int(temp_round_1_game_1[0])
        new_round_1_game_2 = int(temp_round_1_game_2[0])
        new_round_1_game_3 = int(temp_round_1_game_3[0])
        new_round_1_game_4 = int(temp_round_1_game_4[0])

    return render(request, 'home.html', {
        'new_game_1_pick': new_round_1_game_1,
        'new_game_2_pick': new_round_1_game_2,
        'new_game_3_pick': new_round_1_game_3,
        'new_game_4_pick': new_round_1_game_4,
    })
