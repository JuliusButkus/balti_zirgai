from django.shortcuts import render
from . import models
from django.http import HttpRequest


def index(request: HttpRequest):
    num_visits = request.session.get('num_visits', 1)
    request.session['num_visits'] = num_visits + 1
    context = {
        'num_visits': num_visits,
    }
    return render(request, 'alynas/index.html', context)
