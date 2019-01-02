from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from pool.forms import SignUpForm
from pool.models import PickSet
import datetime


round_1_expiration_time = datetime.datetime(2019, 1, 10, 18)
# round_1_expiration_time = datetime.datetime(2018, 12, 29, 21, 41)


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            pick_set = PickSet.objects.create(
                name=user.username,
            )
            return redirect('/picks/edit')
        else:
            return redirect(f'/')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


def profile(request):
    return redirect('/picks')


# Create your views here.
def home_page(request):
    return render(request, 'home.html', {'editing_open': True})


@login_required
def view_picks(request):
    template_to_use = 'picks.html'
    pick_set = PickSet.objects.get(name=request.user.username)
    if pick_set is None:
        pick_set = PickSet.objects.create(
            name=request.user.username,
        )
    if request.user.username != pick_set.name:
        return render(request, 'signup.html', {'form': SignUpForm()})
    return render(request, template_to_use, {
        'pick_set': pick_set,
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
    })


def new_picks(request):
    # FIXME: The 0 default values should be specified elsewhere and read in.
    try:
        temp_name = request.POST['player_name']
    except (KeyError, ValueError):
        temp_name = 'No name'
    pick_set = PickSet.objects.create(
        name=temp_name,
    )
    return redirect(f'/picks/edit')


@login_required
def edit_picks(request):
    pick_set = PickSet.objects.get(name=request.user.username)
    if pick_set is None:
        pick_set = PickSet.objects.create(
            name=request.user.username,
        )
    if request.user.username != pick_set.name:
        return render(request, 'signup.html', {'form': SignUpForm()})
    editing_open = False
    now = datetime.datetime.now()
    if now < round_1_expiration_time:
        editing_open = True
    return render(request, 'edit.html', {
        'pick_set': pick_set,
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'editing_open': editing_open,
    })


@login_required
def update_picks(request):
    pick_set = PickSet.objects.get(name=request.user.username)
    try:
        pick_set.round_1_game_1_team = int(request.POST['game_1_team'])
    except (KeyError, ValueError):
        pass
    try:
        pick_set.round_1_game_1 = int(request.POST['game_1_pick'])
    except (KeyError, ValueError):
        pass
    try:
        pick_set.round_1_game_2_team = int(request.POST['game_2_team'])
    except (KeyError, ValueError):
        pass
    try:
        pick_set.round_1_game_2 = int(request.POST['game_2_pick'])
    except (KeyError, ValueError):
        pass
    try:
        pick_set.round_1_game_3_team = int(request.POST['game_3_team'])
    except (KeyError, ValueError):
        pass
    try:
        pick_set.round_1_game_3 = int(request.POST['game_3_pick'])
    except (KeyError, ValueError):
        pass
    try:
        pick_set.round_1_game_4_team = int(request.POST['game_4_team'])
    except (KeyError, ValueError):
        pass
    try:
        pick_set.round_1_game_4 = int(request.POST['game_4_pick'])
    except (KeyError, ValueError):
        pass
    pick_set.save()
    return redirect(f'/picks/')
