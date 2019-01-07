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

current_matchups = round_1_matchups

started = [False, False, False, False]
finished = [True, True, True, True]
# started = [True, True, True, True]
# finished = [True, True, True, True]
result = [-14, 2, -6, -1]


def update_started():
    if datetime.datetime.now() > datetime.datetime(2019, 1, 5, 21, 30):
        started[0] = True
    if datetime.datetime.now() > datetime.datetime(2019, 1, 6, 1, 10):
        started[1] = True
    if datetime.datetime.now() > datetime.datetime(2019, 1, 6, 18, 00):
        started[2] = True
    if datetime.datetime.now() > datetime.datetime(2019, 1, 6, 21, 30):
        started[3] = True


@login_required
def alternate_view(request):
    pick_set = PickSet.objects.get(name=request.user.username)
    pick_set.results_preference = 1 - pick_set.results_preference
    pick_set.save()
    return redirect('/picks/results/')


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


def results(request, what_if=0):
    try:
        what_if = int(request.GET.get('what_if'))
    except (ValueError, KeyError, TypeError):
        pass
    update_started()
    try:
        pick_set = PickSet.objects.get(name=request.user.username)
        results_pref = pick_set.results_preference
    except PickSet.DoesNotExist:
        results_pref = 0

    data = [
        [
            '', 'Total score',
            current_matchups[0][0] + ' at ' + current_matchups[0][1], '',
            current_matchups[1][0] + ' at ' + current_matchups[1][1], '',
            current_matchups[2][0] + ' at ' + current_matchups[2][1], '',
            current_matchups[3][0] + ' at ' + current_matchups[3][1], '',
        ]
    ]
    data2 = [
        [
            '', 'Total score',
            'Points behind', 'Super Bowl points behind',
        ]
    ]
    row = ['Actual result']
    row = pad_row(row)
    for i in range(4):
        column = 2 * i + 2
        if finished[i]:
            if results_pref == 0:
                if result[i] > 0:
                    team = round_1_matchups[i][1]
                else:
                    team = round_1_matchups[i][0]
                row[column] = team + ' by ' + str(abs(result[i]))
            else:
                row[column] = result[i]
        elif started[i] and (i == 0 or finished[i - 1]) and what_if != 0:
            if results_pref == 0:
                if what_if > 0:
                    team = round_1_matchups[i][1]
                else:
                    team = round_1_matchups[i][0]
                row[column] = 'If ' + team + ' by ' + str(abs(what_if))
            else:
                row[column] = 'If ' + str(what_if)
    data.append(row)

    row = ['']
    row = pad_row(row)
    data.append(row)
    data2.append(row[:4])

    boilerplate_len = len(data)

    for pick in PickSet.objects.all():
        teams = [
            pick.round_1_game_1_team,
            pick.round_1_game_2_team,
            pick.round_1_game_3_team,
            pick.round_1_game_4_team,
        ]
        margins = [
            pick.round_1_game_1,
            pick.round_1_game_2,
            pick.round_1_game_3,
            pick.round_1_game_4,
        ]
        user = User.objects.get(username=pick.name)
        row = [user.first_name + ' ' + user.last_name]
        row = pad_row(row)
        total_score = 0
        for i in range(4):
            if started[i]:
                sign = 2 * teams[i] - 1
                signed_pick = sign * margins[i]
                if results_pref == 0:
                    row[i * 2 + 2] = round_1_matchups[i][teams[i]]
                    row[i * 2 + 2] += ' by ' + str(margins[i])
                else:
                    row[i * 2 + 2] = signed_pick
                if finished[i]:
                    delta = signed_pick - result[i]
                    row[i * 2 + 3] = abs(delta)
                    total_score += abs(delta)
                elif (i == 0 or finished[i - 1]) and what_if != 0:
                    delta = signed_pick - what_if
                    row[i * 2 + 3] = abs(delta)
                    total_score += abs(delta)
        row[1] = total_score

        pbrow = row[:4]
        for i in range(boilerplate_len, len(data)):
            if row[1] < data[i][1]:
                data.insert(i, row)
                data2.insert(i - 1, pbrow)
                break
        else:
            data.append(row)
            data2.append(pbrow)
        for i in range(boilerplate_len - 1, len(data2)):
            data2[i][2] = data2[i][1] - data2[2][1]
            data2[i][3] = str(int(data2[i][2] / 4 + .75))
            if (int(data2[i][2] / 4 + .75)) * 4 == data2[i][2]:
                if data2[i][2] > 0:
                    data2[i][3] += ' to tie'

    return render(request, 'results.html', {
        'data': data, 'whatif': True, 'game_1_started': started[0],
        'game_3_started': false,
        'data2': data2,
    })


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
        'r1g1v': current_matchups[0][0],
        'r1g1h': current_matchups[0][1],
        'r1g2v': current_matchups[1][0],
        'r1g2h': current_matchups[1][1],
        'r1g3v': current_matchups[2][0],
        'r1g3h': current_matchups[2][1],
        'r1g4v': current_matchups[3][0],
        'r1g4h': current_matchups[3][1],
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
        'r1g1v': current_matchups[0][0],
        'r1g1h': current_matchups[0][1],
        'r1g2v': current_matchups[1][0],
        'r1g2h': current_matchups[1][1],
        'r1g3v': current_matchups[2][0],
        'r1g3h': current_matchups[2][1],
        'r1g4v': current_matchups[3][0],
        'r1g4h': current_matchups[3][1],
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
