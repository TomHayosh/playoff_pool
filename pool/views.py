from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from pool.forms import SignUpForm, User
from pool.models import PickSet
import datetime

round_1_matchups = [
    ['Colts', 'Texans'],
    ['Seahawks', 'Cowboys'],
    ['Chargers', 'Ravens'],
    ['Eagles', 'Bears'],
]

started = [False, False, False, False]
finished = [False, False, False, False]
result = [24, -7, 10, 256]


def update_started():
    if datetime.datetime.now() > datetime.datetime(2019, 1, 5, 21, 30):
        started[0] = True
    if datetime.datetime.now() > datetime.datetime(2019, 1, 6, 1, 10):
        started[1] = True
    if datetime.datetime.now() > datetime.datetime(2019, 1, 6, 18, 00):
        started[2] = True
    if datetime.datetime.now() > datetime.datetime(2019, 1, 6, 21, 30):
        started[3] = True


def signup(request):
    update_started()
    if started[0]:
        return home_page(request)
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
                round_1_game_1=1,
                round_1_game_2=2,
                round_1_game_3=3,
                round_1_game_4=6,
            )
            return redirect('/picks/edit')
        else:
            return redirect(f'/')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


def lookup(matchup, key):
    return round_1_matchups[key]


def pad_row(row):
    row.append('')  # For week total
    row.append('')  # For game 1 pick
    row.append('')  # For game 1 delta
    row.append('')  # For game 2 pick
    row.append('')  # For game 2 delta
    row.append('')  # For game 3 pick
    row.append('')  # For game 3 delta
    row.append('')  # For game 4 pick
    row.append('')  # For game 4 delta
    return row


def results(request, whatif=0):
    update_started()
    data = [
        [
            '', 'Total score',
            'Colts at Texans', '',
            'Seahawks at Cowboys', '',
            'Chargers at Ravens', '',
            'Eagles at Bears', '',
        ]
    ]
    row = ['Actual result']
    row = pad_row(row)
    for i in range(4):
        if finished[i]:
            if result[i] > 0:
                team = round_1_matchups[i][1]
            else:
                team = round_1_matchups[i][0]
            column = 2 * i + 2
            row[column] = team + ' by ' + str(abs(result[i]))
    data.append(row)

    row = ['']
    row = pad_row(row)
    data.append(row)

    for pick in PickSet.objects.all():
        user = User.objects.get(username=pick.name)
        row = [user.first_name + ' ' + user.last_name]
        row = pad_row(row)
        total_score = 0
        if started[0]:
            row[2] = round_1_matchups[0][pick.round_1_game_1_team]
            row[2] += ' by ' + str(pick.round_1_game_1)
            if finished[0]:
                sign = pick.round_1_game_1_team * 2 - 1
                signed_pick = sign * pick.round_1_game_1
                delta = signed_pick - result[0]
                row[3] = abs(delta)
                total_score += abs(delta)
        if started[1]:
            row[4] = round_1_matchups[1][pick.round_1_game_2_team]
            row[4] += ' by ' + str(pick.round_1_game_2)
            if finished[1]:
                sign = pick.round_1_game_2_team * 2 - 1
                signed_pick = sign * pick.round_1_game_2
                delta = signed_pick - result[1]
                row[5] = abs(delta)
                total_score += abs(delta)
        if started[2]:
            row[6] = round_1_matchups[2][pick.round_1_game_3_team]
            row[6] += ' by ' + str(pick.round_1_game_3)
            if finished[2]:
                sign = pick.round_1_game_3_team * 2 - 1
                signed_pick = sign * pick.round_1_game_3
                delta = signed_pick - result[2]
                row[7] = abs(delta)
                total_score += abs(delta)
        if started[3]:
            row[8] = round_1_matchups[3][pick.round_1_game_4_team]
            row[8] += ' by ' + str(pick.round_1_game_4)
            if finished[3]:
                sign = pick.round_1_game_4_team * 2 - 1
                signed_pick = sign * pick.round_1_game_4
                delta = signed_pick - result[3]
                row[9] = abs(delta)
                total_score += abs(delta)
        row[1] = total_score
        row_added = False
        for i in range(3, len(data)):
            if row[1] < data[i][1]:
                data.insert(i, row)
                row_added = True
                break
        if not row_added:
            data.append(row)
    return render(request, 'results.html', {'data': data, 'whatif': True})


def profile(request):
    return redirect('/picks')


# Create your views here.
def home_page(request):
    update_started()
    return render(request, 'home.html', {'game_1_started': started[0]})


@login_required
def view_picks(request):
    template_to_use = 'picks.html'
    try:
        pick_set = PickSet.objects.get(name=request.user.username)
    except PickSet.DoesNotExist:
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
    update_started()
    try:
        pick_set = PickSet.objects.get(name=request.user.username)
    except PickSet.DoesNotExist:
        pick_set = PickSet.objects.create(
            name=request.user.username,
        )
    if request.user.username != pick_set.name:
        return render(request, 'signup.html', {'form': SignUpForm()})
    return render(request, 'edit.html', {
        'pick_set': pick_set,
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'game_1_open': not started[0],
        'game_2_open': not started[1],
        'game_3_open': not started[2],
        'game_4_open': not started[3],
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
