from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.
def home_page(request):
    return HttpResponse('<html><title>2019 NFL Playoff Pool</title></html>')
