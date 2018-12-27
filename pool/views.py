from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.
def home_page(request):
    return render(request, 'home.html', {
        'new_game_1_pick': request.POST.get('game_1_pick', ''),
        'new_game_2_pick': request.POST.get('game_2_pick', ''),
        'new_game_3_pick': request.POST.get('game_3_pick', ''),
        'new_game_4_pick': request.POST.get('game_4_pick', ''),
    })
