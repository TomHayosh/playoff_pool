from django.shortcuts import render, redirect
from pool.models import PickSet
import datetime


round_1_expiration_time = datetime.datetime(2019, 1, 10, 18)
# round_1_expiration_time = datetime.datetime(2018, 12, 29, 21, 41)

# Create your views here.
def home_page(request):
    return render(request, 'home.html', {'editing_open': True})


def view_picks(request, pick_set_id):
    template_to_use = 'picks.html'
    pick_set = PickSet.objects.get(id=pick_set_id)
    if pick_set is None:
        return render(request, template_to_use)
    return render(request, template_to_use, {
        'pick_set': pick_set,
    })


def new_picks(request):
    # FIXME: The 0 default values should be specified elsewhere and read in.
    try:
        temp_round_1_game_1 = int(request.POST['game_1_pick'])
    except (KeyError, ValueError):
        temp_round_1_game_1 = 0
    try:
        temp_round_1_game_2 = int(request.POST['game_2_pick'])
    except (KeyError, ValueError):
        temp_round_1_game_2 = 0
    try:
        temp_round_1_game_3 = int(request.POST['game_3_pick'])
    except (KeyError, ValueError):
        temp_round_1_game_3 = 0
    try:
        temp_round_1_game_4 = int(request.POST['game_4_pick'])
    except (KeyError, ValueError):
        temp_round_1_game_4 = 0
    pick_set = PickSet.objects.create(
        round_1_game_1=temp_round_1_game_1,
        round_1_game_2=temp_round_1_game_2,
        round_1_game_3=temp_round_1_game_3,
        round_1_game_4=temp_round_1_game_4,
    )
    return redirect(f'/picks/{pick_set.id}/')


def edit_picks(request, pick_set_id):
    editing_open = False
    pick_set = PickSet.objects.get(id=pick_set_id)
    now = datetime.datetime.now()
    if now < round_1_expiration_time:
        editing_open = True
    return render(request, 'edit.html', {
        'pick_set': pick_set,
        'editing_open': editing_open,
    })


def update_picks(request, pick_set_id):
    pick_set = PickSet.objects.get(id=pick_set_id)
    try:
        pick_set.round_1_game_1 = int(request.POST['game_1_pick'])
    except (KeyError, ValueError):
        pass
    try:
        pick_set.round_1_game_2 = int(request.POST['game_2_pick'])
    except (KeyError, ValueError):
        pass
    try:
        pick_set.round_1_game_3 = int(request.POST['game_3_pick'])
    except (KeyError, ValueError):
        pass
    try:
        pick_set.round_1_game_4 = int(request.POST['game_4_pick'])
    except (KeyError, ValueError):
        pass
    pick_set.save()
    return redirect(f'/picks/{pick_set.id}/')
