from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from pool.forms import SignUpForm, User
from pool.models import PickSet
import datetime
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import json
import time
import random

num_games = (4, 2, 1)
last_nfl_request = [time.time() - 180]

wild_card_matchups = [
    ['Colts', 'Texans', datetime.datetime(2019, 1, 5, 15, 30), 'NBC'],
    ['Seahawks', 'Cowboys', datetime.datetime(2019, 1, 5, 19, 10), 'FOX'],
    ['Chargers', 'Ravens', datetime.datetime(2019, 1, 6, 12, 00), 'CBS'],
    ['Eagles', 'Bears', datetime.datetime(2019, 1, 6, 15, 30), 'ESPN'],
]
wild_card_starts = [True, True, True, True]
wild_card_in_progress = [False, False, False, False]
wild_card_finished = [True, True, True, True]
wild_card_result = [-14, 2, -6, -1]


divisional_matchups = [
    ['Colts', 'Chiefs', datetime.datetime(2019, 1, 12, 15, 30), 'NBC'],
    ['Cowboys', 'Rams', datetime.datetime(2019, 1, 12, 19, 10), 'FOX'],
    ['Chargers', 'Patriots', datetime.datetime(2019, 1, 13, 12, 00), 'CBS'],
    ['Eagles', 'Saints', datetime.datetime(2019, 1, 13, 15, 35), 'FOX'],
]
divisional_starts = [True, True, True, True]
divisional_in_progress = [False, False, False, False]
divisional_finished = [True, True, True, True]
# divisional_starts = [True, True, True, True]
# divisional_finished = [True, True, True, True]
# divisional_result = [-19, -19, 5, 11]
divisional_result = [18, 8, 13, 6]

conference_matchups = [
    ['Rams', 'Saints', datetime.datetime(2019, 1, 20, 14, 00), 'FOX'],
    ['Patriots', 'Chiefs', datetime.datetime(2019, 1, 20, 17, 35), 'CBS'],
]
conference_starts = [True, True]
conference_in_progress = [False, False, False, False]
conference_finished = [True, True]
conference_result = [-3, -6]

sb_matchups = [
    ['Patriots', 'Rams', datetime.datetime(2019, 2, 3, 17, 30), 'CBS'],
]
sb_starts = [True]
sb_in_progress = [False, False, False, False]
sb_finished = [True]
sb_result = [-10]

current_matchups = divisional_matchups

current_pick_set_object = PickSet


def date_string(dt):
    hour = (dt.hour + -1) % 12 + 1
    daynum = dt.day
    return dt.strftime(
        str(hour) + ':%M %p ' + 'CST' + ' %A, %B, ' + str(daynum)
    )


def kickoff(game):
    return date_string(game[2]) + ' ' + game[3]


def update_starts():
    for i in range(num_games[0]):
        if datetime.datetime.now() > divisional_matchups[i][2]:
            divisional_starts[i] = True
    for i in range(num_games[1]):
        if datetime.datetime.now() > conference_matchups[i][2]:
            conference_starts[i] = True
    for i in range(num_games[2]):
        if datetime.datetime.now() > sb_matchups[i][2]:
            sb_starts[i] = True


@login_required
def alternate_view(request):
    pick_set = current_pick_set_object.objects.get(name=request.user.username)
    pick_set.results_preference = 1 - pick_set.results_preference
    pick_set.save()
    return redirect('/picks/results/')


def signup(request):
    update_starts()
    if divisional_starts[0]:
        return home_page(request)
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            pick_set = current_pick_set_object.objects.create(
                name=user.username,
                round_1_game_1=6,  # 1,
                round_1_game_2=5,  # 2,
                round_1_game_3=5,  # 3,
                round_1_game_4=11,  # 6,
            )
            return redirect('/picks/edit')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


def pad_row(row, padding_size):
    for i in range(padding_size):
        row.append('')
    return row


def migrate_picks():
    for pick_set in PickSet.objects.all():
        if (pick_set.round_1_game_1 == 1000):
            return
    for pick_set in PickSet.objects.all():
        pick_set.wc_game_1_team = pick_set.round_1_game_1_team
        pick_set.wc_game_2_team = pick_set.round_1_game_2_team
        pick_set.wc_game_3_team = pick_set.round_1_game_3_team
        pick_set.wc_game_4_team = pick_set.round_1_game_4_team
        pick_set.wc_game_1 = pick_set.round_1_game_1
        pick_set.wc_game_2 = pick_set.round_1_game_2
        pick_set.wc_game_3 = pick_set.round_1_game_3
        pick_set.wc_game_4 = pick_set.round_1_game_4
        pick_set.round_1_game_1_team = 1
        pick_set.round_1_game_2_team = 1
        pick_set.round_1_game_3_team = 1
        pick_set.round_1_game_4_team = 1
        pick_set.round_1_game_1 = 1000
        pick_set.round_1_game_2 = 5
        pick_set.round_1_game_3 = 5
        pick_set.round_1_game_4 = 11
        pick_set.save()


def generate_results(
    teams, margins, started, finished, what_if, h_boilerplate, result,
    row, total_col, results_pref, the_matchups, game_count, in_progress
):
    total_score = 0
    for i in range(game_count):
        if started[i]:
            sign = 2 * teams[i] - 1
            signed_pick = sign * margins[i]
            column = i * 2 + h_boilerplate
            if results_pref == 0:
                row[column] = the_matchups[i][teams[i]]
                row[column] += ' by ' + str(margins[i])
            else:
                row[column] = signed_pick
            column = i * 2 + h_boilerplate + 1
            if finished[i]:
                delta = signed_pick - result[i]
                row[column] = abs(delta)
                total_score += abs(delta)
            elif (i == 0 or finished[i - 1]) and what_if != 0:
                delta = signed_pick - what_if
                row[column] = abs(delta)
                total_score += abs(delta)
            elif in_progress[i]:
                delta = signed_pick - result[i]
                row[column] = abs(delta)
                total_score += abs(delta)
    row[total_col] = total_score


def is_good_response(resp):
    content_type = resp.headers['Content-Type'].lower()
    print(content_type)
    return (resp.status_code == 200 and
            content_type is not None and
            content_type.find('html') > -1)


def simple_get(url):
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None
    except RequestException as e:
        print('Error during requests to {0}: {1}'.format(url, str(e)))
        return None


def load_bjcp_json():
    try:
        file = open('styleguide-2015.min.json')
        content_string = file.read()
        bjcp_json = json.loads(content_string)
        file.close()
        return bjcp_json
    except FileNotFoundError:
        file = open('testfile.txt', 'w')
        file.write('Hello')
        file.close()
        raw_html = simple_get('https://github.com/gthmb/bjcp-2015-json/blob/master/json/styleguide-2015.min.json')
        html = BeautifulSoup(raw_html, 'html.parser')
        content_string = html.decode_contents()
        start_location = content_string.find('{"styleguide')
        end_location = content_string.find('</td>', start_location)
        y = json.loads(content_string[start_location: end_location])
        return y


def bjcp_all(request):
    bjcp_json = load_bjcp_json()
    text_from_page = ''
    test_subcats = []
    for category in bjcp_json['styleguide']['class'][0]['category']:
        if int(category['id']) > 26:
            continue
        for subcat in category['subcategory']:
            # elif category['name'] == 'American IPA':
            if '21B' not in subcat['id'] and subcat['id'] != '7C':
                test_subcats.append(subcat)
    # for subcat in test_subcats:
    subcat = random.choice(test_subcats)
    og = subcat['stats']['og']
    data = []
    row = [
        '', 'BJCP ID', 'Name', 'OG Low', 'OG High', 'FG Low', 'FG High',
        'IBU Low', 'IBU High', 'SRM Low', 'SRM High', 'ABV Low', 'ABV High'
    ]
    data.append(row)
    subcat_index = 1
    for category in bjcp_json['styleguide']['class'][0]['category']:
        if int(category['id']) > 26:
            continue
        for subcat2 in category['subcategory']:
            # if category['name'] == 'American IPA':
            if '21B' not in subcat2['id'] and subcat2['id'] != '7C':
                row = [subcat_index, subcat2['id'], subcat2['name']]
                subcat_index += 1
                stat = subcat['stats']
                for key in subcat2['stats']:
                    row.append(subcat2['stats'][key]['low'])
                    row.append(subcat2['stats'][key]['high'])
                data.append(row)
    return render(request, 'bjcp.html', {
        'subcat_id': subcat['id'],
        'subcat_name': subcat['name'],
        'og_high': subcat['stats']['og']['high'],
        'og_low': subcat['stats']['og']['low'],
        'ibu_high': subcat['stats']['ibu']['high'],
        'ibu_low': subcat['stats']['ibu']['low'],
        'abv_high': subcat['stats']['abv']['high'],
        'abv_low': subcat['stats']['abv']['low'],
        'srm_high': subcat['stats']['srm']['high'],
        'srm_low': subcat['stats']['srm']['low'],
        'data': data,
    })


def bjcp(request):
    # def bjcp_comparables(request):
    bjcp_json = load_bjcp_json()
    text_from_page = ''
    test_subcats = []
    for category in bjcp_json['styleguide']['class'][0]['category']:
        if int(category['id']) > 26:
            continue
        for subcat in category['subcategory']:
            # elif category['name'] == 'American IPA':
            if '21B' not in subcat['id'] and subcat['id'] != '7C':
                test_subcats.append(subcat)
    # for subcat in test_subcats:
    subcat = None
    try:
        subcat_id = request.GET.get('subcat')
        for item in test_subcats:
            if item['id'] == subcat_id:
                subcat = item
                break
    except (ValueError, KeyError, TypeError):
        pass
    if subcat is None:
        subcat = random.choice(test_subcats)
    og = subcat['stats']['og']
    data = []
    row = ['', '', 'OG L', 'OG H', 'FG L', 'FG H', 'IBU L', 'IBU H', 'SRM L',
        'SRM H', 'ABV L', 'ABV H']
    data.append(row)
    for category in bjcp_json['styleguide']['class'][0]['category']:
        if int(category['id']) > 26:
            continue
        for subcat2 in category['subcategory']:
            # if category['name'] == 'American IPA':
            if '21B' not in subcat2['id'] and subcat2['id'] != '7C':
                overlaps = 0
                row = [subcat2['id'], subcat2['name']]
                stat = subcat['stats']
                for key in subcat2['stats']:
                    value_high = float(subcat2['stats'][key]['high'])
                    value_low = float(subcat2['stats'][key]['low'])
                    high = float(stat[key]['high'])
                    low = float(stat[key]['low'])
                    row.append(subcat2['stats'][key]['low'])
                    row.append(subcat2['stats'][key]['high'])
                    if (value_low >= low and value_low < high or
                            value_high > low and value_high <= high or
                            value_low <= low and value_high >= high or
                            value_low >= low and value_high <= high):
                        if key in ('og', 'ibu', 'srm'):
                            overlaps += 1
                if (overlaps == 3):
                    data.append(row)
    return render(request, 'bjcp.html', {
        'subcat_id': subcat['id'],
        'subcat_name': subcat['name'],
        'og_high': subcat['stats']['og']['high'],
        'og_low': subcat['stats']['og']['low'],
        'ibu_high': subcat['stats']['ibu']['high'],
        'ibu_low': subcat['stats']['ibu']['low'],
        'abv_high': subcat['stats']['abv']['high'],
        'abv_low': subcat['stats']['abv']['low'],
        'srm_high': subcat['stats']['srm']['high'],
        'srm_low': subcat['stats']['srm']['low'],
        'data': data,
    })


def update_request_time():
    last_nfl_request[0] = time.time()
    print(f'Request time after {last_nfl_request[0]}')


def too_soon_to_request_nfl():
    print(f'Request time before {last_nfl_request[0]}')
    seconds_elapsed = time.time() - last_nfl_request[0]
    print(seconds_elapsed)
    return seconds_elapsed < 10


def scrape_nfl_dot_com_strip():
    if too_soon_to_request_nfl():
        # print(f'Returning - only {seconds_elapsed} seconds have passed.')
        print('Returning')
        return
    update_request_time()
    raw_html = simple_get('https://www.nfl.com/')
    html = BeautifulSoup(raw_html, 'html.parser')
    content_string = html.decode_contents()
    start_location = content_string.find('__INITIAL_DATA__')
    json_start = content_string.find('{', start_location)
    json_end = content_string.find('\n', json_start)
    start_location = content_string.find('__REACT_ROOT_ID__')
    # Subtract 1 to remove the semicolon that ends the Javascript statement
    y = json.loads(content_string[json_start: json_end - 1])
    # print(json.dumps(y))
    for game in y['uiState']['scoreStripGames']:
        # FIXME: range length must not be hard coded
        for i in range(1):
            # print(f"{game['awayTeam']['identifier']}")
            # print(f"{conference_matchups[i][0]}")
            if game['awayTeam']['identifier'] == sb_matchups[i][0]:
                status = game['status']
                # print(status)
                if not status['isUpcoming']:
                    # print('Not upcoming')
                    if status['phaseDescription'] == 'FINAL':
                        print(f"{game['awayTeam']['identifier']} finished")
                        sb_finished[i] = True
                        home_score = game['homeTeam']['scores']['pointTotal']
                        away_score = game['awayTeam']['scores']['pointTotal']
                        delta = home_score - away_score
                        # print(f'Delta is {delta}')
                        sb_result[i] = delta
                    in_progress = status['isInProgress']
                    # print(in_progress)
                    in_progress_overtime = status['isInProgressOvertime']
                    # print(in_progress_overtime)
                    in_half = status['isHalf']
                    # print(in_half)
                    if in_progress or in_progress_overtime or in_half:
                        home_score = game['homeTeam']['scores']['pointTotal']
                        away_score = game['awayTeam']['scores']['pointTotal']
                        delta = home_score - away_score
                        # print(f'Delta is {delta}')
                        sb_result[i] = delta
                        sb_in_progress[i] = True
                    # else:
                    #     sb_in_progress[i] = False


def nfl(request):
    scrape_nfl_dot_com_strip()
    return results_sb(request)


def results(request, wc_as_1=False):
    # bjcp_quiz()
    # migrate_picks()
    what_if = 0
    try:
        what_if = int(request.GET.get('what_if'))
    except (ValueError, KeyError, TypeError):
        pass
    update_starts()
    try:
        pick_set = current_pick_set_object.objects.get(
            name=request.user.username
        )
        results_pref = pick_set.results_preference
    except current_pick_set_object.DoesNotExist:
        results_pref = 0

    if wc_as_1:
        the_matchups = wild_card_matchups
        started = wild_card_starts
        finished = wild_card_finished
        in_progress = wild_card_in_progress
    else:
        the_matchups = divisional_matchups
        started = divisional_starts
        finished = divisional_finished
        in_progress = divisional_in_progress
    data = [
        [
            '', 'Total score',
            the_matchups[0][0] + ' at ' + the_matchups[0][1], '',
            the_matchups[1][0] + ' at ' + the_matchups[1][1], '',
            the_matchups[2][0] + ' at ' + the_matchups[2][1], '',
            the_matchups[3][0] + ' at ' + the_matchups[3][1], '',
        ]
    ]
    h_boilerplate = 2
    data2 = [
        [
            '', 'Total score',
            'Points behind', 'Super Bowl points behind',
        ]
    ]
    row = ['Actual result']
    row = pad_row(row, len(data[0]) - 1)
    if wc_as_1:
        result = wild_card_result
    else:
        result = divisional_result
    for i in range(num_games[0]):
        column = 2 * i + h_boilerplate
        if finished[i]:
            if results_pref == 0:
                if result[i] > 0:
                    team = the_matchups[i][1]
                else:
                    team = the_matchups[i][0]
                row[column] = team + ' by ' + str(abs(result[i]))
            else:
                row[column] = result[i]
        elif started[i] and (i == 0 or finished[i - 1]) and what_if != 0:
            if results_pref == 0:
                if what_if > 0:
                    team = the_matchups[i][1]
                else:
                    team = the_matchups[i][0]
                row[column] = 'If ' + team + ' by ' + str(abs(what_if))
            else:
                row[column] = 'If ' + str(what_if)
        elif not wc_as_1 and in_progress[i]:
            if results_pref == 0:
                if result[i] > 0:
                    team = the_matchups[i][1]
                else:
                    team = the_matchups[i][0]
                row[column] = "In progress: "
                if result[i] == 0:
                    row[column] += 'Tied'
                else:
                    row[column] += team + ' by ' + str(abs(result[i]))
            else:
                row[column] = "In progress: " + str(result[i])
    data.append(row)

    row = ['']
    row = pad_row(row, len(data[0]) - 1)
    data.append(row)
    data2.append(row[:4])

    boilerplate_len = len(data)

    for pick in current_pick_set_object.objects.all():
        if pick.round_1_game_1 == 1000:
            continue
        if wc_as_1:
            teams = [
                pick.wc_game_1_team,
                pick.wc_game_2_team,
                pick.wc_game_3_team,
                pick.wc_game_4_team,
            ]
            margins = [
                pick.wc_game_1,
                pick.wc_game_2,
                pick.wc_game_3,
                pick.wc_game_4,
            ]
        else:
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
        row = pad_row(row, len(data[0]) - 1)
        total_col = 1
        temp_row = ['']
        temp_row = pad_row(temp_row, len(data[0]) - 1)
        generate_results(
            teams, margins, started, finished, what_if, h_boilerplate,
            result, temp_row, total_col, results_pref, the_matchups,
            num_games[0], in_progress
        )
        row[1:len(data[0])] = temp_row[1:len(data[0])]

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
        'playoff_week': 'Week 1',
        'data': data, 'whatif': True, 'game_1_started': started[0],
        # The game_3_started variable really should be show_what_if
        'game_3_started': started[2] and not finished[num_games[0] - 1],
        # 'game_3_started': False,
        'data2': data2,
    })


def results_week2(request, wc_as_1=False):
    # bjcp_quiz()
    # migrate_picks()
    what_if = 0
    try:
        what_if = int(request.GET.get('what_if'))
    except (ValueError, KeyError, TypeError):
        pass
    update_starts()
    try:
        pick_set = current_pick_set_object.objects.get(
            name=request.user.username
        )
        results_pref = pick_set.results_preference
    except current_pick_set_object.DoesNotExist:
        results_pref = 0

    if wc_as_1:
        # Diff from results
        the_matchups = divisional_matchups
        started = divisional_starts
        finished = divisional_finished
        in_progress = divisional_in_progress
        prev_matchups = wild_card_matchups
        prev_started = wild_card_starts
        prev_finished = wild_card_finished
    else:
        the_matchups = conference_matchups
        started = conference_starts
        finished = conference_finished
        in_progress = conference_in_progress
        prev_matchups = divisional_matchups
        prev_started = divisional_starts
        prev_finished = divisional_finished
        # End diff from results
    data = [
        [
            '', 'Total score', 'Week 1 subtotal', 'Week 2 score',
            the_matchups[0][0] + ' at ' + the_matchups[0][1], '',
            the_matchups[1][0] + ' at ' + the_matchups[1][1], '',
        ]
    ]
    h_boilerplate = 4
    data2 = [
        [
            '', 'Total score',
            'Points behind', 'Super Bowl points behind',
        ]
    ]
    row = ['Actual result']
    row = pad_row(row, len(data[0]) - 1)
    if wc_as_1:
        prev_result = wild_card_result
        result = divisional_result
    else:
        prev_result = divisional_result
        result = conference_result
    for i in range(num_games[1]):
        column = 2 * i + h_boilerplate
        if finished[i]:
            if results_pref == 0:
                if result[i] > 0:
                    team = the_matchups[i][1]
                else:
                    team = the_matchups[i][0]
                row[column] = team + ' by ' + str(abs(result[i]))
            else:
                row[column] = result[i]
        elif started[i] and (i == 0 or finished[i - 1]) and what_if != 0:
            if results_pref == 0:
                if what_if > 0:
                    team = the_matchups[i][1]
                else:
                    team = the_matchups[i][0]
                row[column] = 'If ' + team + ' by ' + str(abs(what_if))
            else:
                row[column] = 'If ' + str(what_if)
        elif not wc_as_1 and in_progress[i]:
            if results_pref == 0:
                if result[i] > 0:
                    team = the_matchups[i][1]
                else:
                    team = the_matchups[i][0]
                row[column] = "In progress: "
                if result[i] == 0:
                    row[column] += 'Tied'
                else:
                    row[column] += team + ' by ' + str(abs(result[i]))
            else:
                row[column] = "In progress: " + str(result[i])
    data.append(row)

    row = ['']
    row = pad_row(row, len(data[0]) - 1)
    data.append(row)
    data2.append(row[:4])

    boilerplate_len = len(data)

    for pick in current_pick_set_object.objects.all():
        if pick.round_1_game_1 == 1000:
            continue
        if wc_as_1:
            teams = [
                pick.round_1_game_1_team,
                pick.round_1_game_2_team,
            ]
            margins = [
                pick.round_1_game_1,
                pick.round_1_game_2,
            ]
            prev_teams = [
                pick.wc_game_1_team,
                pick.wc_game_2_team,
                pick.wc_game_3_team,
                pick.wc_game_4_team,
            ]
            prev_margins = [
                pick.wc_game_1,
                pick.wc_game_2,
                pick.wc_game_3,
                pick.wc_game_4,
            ]
        else:
            # FIXME: Update values below with conference round picks
            teams = [
                pick.round_2_game_1_team,
                pick.round_2_game_2_team,
            ]
            margins = [
                pick.round_2_game_1,
                pick.round_2_game_2,
            ]
            prev_teams = [
                pick.round_1_game_1_team,
                pick.round_1_game_2_team,
                pick.round_1_game_3_team,
                pick.round_1_game_4_team,
            ]
            prev_margins = [
                pick.round_1_game_1,
                pick.round_1_game_2,
                pick.round_1_game_3,
                pick.round_1_game_4,
            ]
        user = User.objects.get(username=pick.name)
        row = [user.first_name + ' ' + user.last_name]
        row = pad_row(row, len(data[0]) - 1)
        total_col = 3
        temp_row = ['']
        temp_row = pad_row(temp_row, len(data[0]) - 1)
        generate_results(
            teams, margins, started, finished, what_if, h_boilerplate,
            result, temp_row, total_col, results_pref, the_matchups,
            num_games[1], in_progress
        )
        row[1:len(data[0])] = temp_row[1:len(data[0])]
        row[3] = 2 * row[3]
        temp_row = ['']
        # FIXME - 11 because h_boilerplate is from week 2, not week 1
        temp_row = pad_row(temp_row, 11)
        total_col = 1
        generate_results(
            prev_teams, prev_margins, prev_started, prev_finished, what_if,
            h_boilerplate, prev_result, temp_row, total_col, results_pref,
            prev_matchups, num_games[0], in_progress
        )
        row[2] = temp_row[total_col]
        row[1] = row[2] + row[3]

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
        'playoff_week': 'Week 2',
        'data': data, 'whatif': True, 'game_1_started': started[0],
        # The game_3_started variable really should be show_what_if
        'game_3_started': started[0] and not finished[num_games[1] - 1],
        # 'game_3_started': False,
        'data2': data2,
    })


def results_sb(request, wc_as_1=False):
    # bjcp_quiz()
    # migrate_picks()
    what_if = 0
    try:
        what_if = int(request.GET.get('what_if'))
    except (ValueError, KeyError, TypeError):
        pass
    update_starts()
    try:
        pick_set = current_pick_set_object.objects.get(
            name=request.user.username
        )
        results_pref = pick_set.results_preference
    except current_pick_set_object.DoesNotExist:
        results_pref = 0

    if wc_as_1:
        # Diff from results
        the_matchups = conference_matchups
        started = conference_starts
        finished = conference_finished
        in_progress = conference_in_progress
        prev_matchups = divisional_matchups
        prev_started = divisional_starts
        prev_finished = divisional_finished
        first_matchups = wild_card_matchups
        first_started = wild_card_starts
        first_finished = wild_card_finished
    else:
        the_matchups = sb_matchups
        started = sb_starts
        finished = sb_finished
        in_progress = sb_in_progress
        prev_matchups = conference_matchups
        prev_started = conference_starts
        prev_finished = conference_finished
        first_matchups = divisional_matchups
        first_started = divisional_starts
        first_finished = divisional_finished
        # End diff from results
    data = [
        [
            '', 'Total score', 'Subtotal after Week 2', 'Super Bowl score',
            the_matchups[0][0] + ' at ' + the_matchups[0][1],
            'Super Bowl difference',
        ]
    ]
    h_boilerplate = 4
    data2 = [
        [
            '', 'Total score',
            'Points behind', 'Super Bowl points behind',
        ]
    ]
    row = ['Actual result']
    row = pad_row(row, len(data[0]) - 1)
    if wc_as_1:
        first_result = wild_card_result
        prev_result = divisional_result
        result = conference_result
    else:
        first_result = divisional_result
        prev_result = conference_result
        result = sb_result
    for i in range(num_games[2]):
        column = 2 * i + h_boilerplate
        if finished[i]:
            if results_pref == 0:
                if result[i] > 0:
                    team = the_matchups[i][1]
                else:
                    team = the_matchups[i][0]
                row[column] = team + ' by ' + str(abs(result[i]))
            else:
                row[column] = result[i]
        elif started[i] and (i == 0 or finished[i - 1]) and what_if != 0:
            if results_pref == 0:
                if what_if > 0:
                    team = the_matchups[i][1]
                else:
                    team = the_matchups[i][0]
                row[column] = 'If ' + team + ' by ' + str(abs(what_if))
            else:
                row[column] = 'If ' + str(what_if)
        elif not wc_as_1 and in_progress[i]:
            if results_pref == 0:
                if result[i] > 0:
                    team = the_matchups[i][1]
                else:
                    team = the_matchups[i][0]
                row[column] = "In progress: "
                if result[i] == 0:
                    row[column] += 'Tied'
                else:
                    row[column] += team + ' by ' + str(abs(result[i]))
            else:
                row[column] = "In progress: " + str(result[i])
    data.append(row)

    row = ['']
    row = pad_row(row, len(data[0]) - 1)
    data.append(row)
    data2.append(row[:4])

    boilerplate_len = len(data)

    for pick in current_pick_set_object.objects.all():
        if pick.round_1_game_1 == 1000:
            continue
        if wc_as_1:
            teams = [
                pick.round_2_game_1_team,
            ]
            margins = [
                pick.round_2_game_1,
            ]
            prev_teams = [
                pick.round_1_game_1_team,
                pick.round_1_game_2_team,
            ]
            prev_margins = [
                pick.round_1_game_1,
                pick.round_1_game_2,
            ]
            first_teams = [
                pick.wc_game_1_team,
                pick.wc_game_2_team,
                pick.wc_game_3_team,
                pick.wc_game_4_team,
            ]
            first_margins = [
                pick.wc_game_1,
                pick.wc_game_2,
                pick.wc_game_3,
                pick.wc_game_4,
            ]
        else:
            # FIXME: Update values below with Super Bowl picks
            teams = [
                pick.super_bowl_team,
            ]
            margins = [
                pick.super_bowl_pick,
            ]
            prev_teams = [
                pick.round_2_game_1_team,
                pick.round_2_game_2_team,
            ]
            prev_margins = [
                pick.round_2_game_1,
                pick.round_2_game_2,
            ]
            first_teams = [
                pick.round_1_game_1_team,
                pick.round_1_game_2_team,
                pick.round_1_game_3_team,
                pick.round_1_game_4_team,
            ]
            first_margins = [
                pick.round_1_game_1,
                pick.round_1_game_2,
                pick.round_1_game_3,
                pick.round_1_game_4,
            ]
        user = User.objects.get(username=pick.name)
        row = [user.first_name + ' ' + user.last_name]
        row = pad_row(row, len(data[0]) - 1)
        total_col = 3
        temp_row = ['']
        temp_row = pad_row(temp_row, len(data[0]) - 1)
        generate_results(
            teams, margins, started, finished, what_if, h_boilerplate,
            result, temp_row, total_col, results_pref, the_matchups,
            num_games[2], in_progress
        )
        row[1:len(data[0])] = temp_row[1:len(data[0])]
        temp_row = ['']
        # FIXME - 11 because h_boilerplate is from week 2, not week 1
        temp_row = pad_row(temp_row, 9)
        total_col = 1
        generate_results(
            prev_teams, prev_margins, prev_started, prev_finished, what_if,
            h_boilerplate, prev_result, temp_row, total_col, results_pref,
            prev_matchups, num_games[1], in_progress
        )
        round_2_score = temp_row[total_col]
        temp_row = ['']
        # FIXME - 11 because h_boilerplate is from week 2, not week 1
        temp_row = pad_row(temp_row, 11)
        total_col = 1
        generate_results(
            first_teams, first_margins, first_started, first_finished, what_if,
            h_boilerplate, first_result, temp_row, total_col, results_pref,
            first_matchups, num_games[0], in_progress
        )
        row[2] = temp_row[total_col] + round_2_score * 2
        row[3] = row[3] * 4
        row[1] = row[2] + row[3]

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
        'playoff_week': 'Super Bowl',
        'data': data, 'whatif': True, 'game_1_started': started[0],
        # The game_3_started variable really should be show_what_if
        'game_3_started': started[0] and not finished[num_games[2] - 1],
        # 'game_3_started': False,
        'data2': data2,
    })


def round2test1(request):
    return results(request, wc_as_1=True)


def round2test2(request):
    return results_week2(request, wc_as_1=True)


def sbtest(request):
    return results_sb(request, wc_as_1=True)


def profile(request):
    return redirect('/picks')


# Create your views here.
def home_page(request):
    update_starts()
    return render(request, 'home.html', {
        'game_1_started': divisional_starts[0]
    })


@login_required
def view_picks3(request):
    template_to_use = 'picks3.html'
    try:
        pick_set = current_pick_set_object.objects.get(
            name=request.user.username
        )
    except current_pick_set_object.DoesNotExist:
        pick_set = current_pick_set_object.objects.create(
            name=request.user.username,
        )
    if request.user.username != pick_set.name:
        return render(request, 'signup.html', {'form': SignUpForm()})
    return render(request, template_to_use, {
        'pick_set': pick_set,
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'r2g1v': sb_matchups[0][0],
        'r2g1h': sb_matchups[0][1],
        'r2g1ko': kickoff(sb_matchups[0]),
        'game_1_open': not sb_starts[0],
    })


@login_required
def view_picks2(request):
    template_to_use = 'picks2.html'
    try:
        pick_set = current_pick_set_object.objects.get(
            name=request.user.username
        )
    except current_pick_set_object.DoesNotExist:
        pick_set = current_pick_set_object.objects.create(
            name=request.user.username,
        )
    if request.user.username != pick_set.name:
        return render(request, 'signup.html', {'form': SignUpForm()})
    return render(request, template_to_use, {
        'pick_set': pick_set,
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'r2g1v': conference_matchups[0][0],
        'r2g1h': conference_matchups[0][1],
        'r2g2v': conference_matchups[1][0],
        'r2g2h': conference_matchups[1][1],
        'r2g1ko': kickoff(conference_matchups[0]),
        'r2g2ko': kickoff(conference_matchups[1]),
        'game_1_open': not conference_starts[0],
        'game_2_open': not conference_starts[1],
    })


@login_required
def view_picks(request):
    template_to_use = 'picks.html'
    try:
        pick_set = current_pick_set_object.objects.get(
            name=request.user.username
        )
    except current_pick_set_object.DoesNotExist:
        pick_set = current_pick_set_object.objects.create(
            name=request.user.username,
        )
    if request.user.username != pick_set.name:
        return render(request, 'signup.html', {'form': SignUpForm()})
    return render(request, template_to_use, {
        'pick_set': pick_set,
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'r1g1v': divisional_matchups[0][0],
        'r1g1h': divisional_matchups[0][1],
        'r1g2v': divisional_matchups[1][0],
        'r1g2h': divisional_matchups[1][1],
        'r1g3v': divisional_matchups[2][0],
        'r1g3h': divisional_matchups[2][1],
        'r1g4v': divisional_matchups[3][0],
        'r1g4h': divisional_matchups[3][1],
        'r1g1ko': kickoff(divisional_matchups[0]),
        'r1g2ko': kickoff(divisional_matchups[1]),
        'r1g3ko': kickoff(divisional_matchups[2]),
        'r1g4ko': kickoff(divisional_matchups[3]),
    })


def new_picks(request):
    # FIXME: The 0 default values should be specified elsewhere and read in.
    try:
        temp_name = request.POST['player_name']
    except (KeyError, ValueError):
        temp_name = 'No name'
    pick_set = current_pick_set_object.objects.create(
        name=temp_name,
    )
    return redirect(f'/picks/edit')


@login_required
def edit_picks(request):
    update_starts()
    try:
        pick_set = current_pick_set_object.objects.get(
            name=request.user.username
        )
    except current_pick_set_object.DoesNotExist:
        pick_set = current_pick_set_object.objects.create(
            name=request.user.username,
        )
    if request.user.username != pick_set.name:
        return render(request, 'signup.html', {'form': SignUpForm()})
    started = divisional_starts
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
        'r1g1ko': kickoff(current_matchups[0]),
        'r1g2ko': kickoff(current_matchups[1]),
        'r1g3ko': kickoff(current_matchups[2]),
        'r1g4ko': kickoff(current_matchups[3]),
    })


@login_required
def update_picks3(request):
    pick_set = current_pick_set_object.objects.get(name=request.user.username)
    started = sb_starts
    # FIXME: Test the started conditionals!!!
    if not started[0]:
        try:
            pick_set.super_bowl_team = int(request.POST['game_1_team'])
        except (KeyError, ValueError):
            pass
        try:
            pick_set.super_bowl_pick = int(request.POST['game_1_pick'])
        except (KeyError, ValueError):
            pass
    pick_set.save()
    return redirect(f'/picks/sb_pick/')


@login_required
def update_picks2(request):
    pick_set = current_pick_set_object.objects.get(name=request.user.username)
    started = conference_starts
    # FIXME: Test the started conditionals!!!
    if not started[0]:
        try:
            pick_set.round_2_game_1_team = int(request.POST['game_1_team'])
        except (KeyError, ValueError):
            pass
        try:
            pick_set.round_2_game_1 = int(request.POST['game_1_pick'])
        except (KeyError, ValueError):
            pass
    if not started[1]:
        try:
            pick_set.round_2_game_2_team = int(request.POST['game_2_team'])
        except (KeyError, ValueError):
            pass
        try:
            pick_set.round_2_game_2 = int(request.POST['game_2_pick'])
        except (KeyError, ValueError):
            pass
    pick_set.save()
    return redirect(f'/picks/week2/')


@login_required
def update_picks(request):
    pick_set = current_pick_set_object.objects.get(name=request.user.username)
    started = divisional_starts
    # FIXME: Test the started conditionals!!!
    if not started[0]:
        try:
            pick_set.round_1_game_1_team = int(request.POST['game_1_team'])
        except (KeyError, ValueError):
            pass
        try:
            pick_set.round_1_game_1 = int(request.POST['game_1_pick'])
        except (KeyError, ValueError):
            pass
    if not started[1]:
        try:
            pick_set.round_1_game_2_team = int(request.POST['game_2_team'])
        except (KeyError, ValueError):
            pass
        try:
            pick_set.round_1_game_2 = int(request.POST['game_2_pick'])
        except (KeyError, ValueError):
            pass
    if not started[2]:
        try:
            pick_set.round_1_game_3_team = int(request.POST['game_3_team'])
        except (KeyError, ValueError):
            pass
        try:
            pick_set.round_1_game_3 = int(request.POST['game_3_pick'])
        except (KeyError, ValueError):
            pass
    if not started[3]:
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
