from typing import Any
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest
from django.db.models.query import QuerySet, Q
from django.shortcuts import render, get_object_or_404
from django.views import generic
from . import models
from .models import Beer
from django.db.models import Sum


def index(request: HttpRequest):
    num_visits = request.session.get('num_visits', 1)
    request.session['num_visits'] = num_visits + 1
    total_qty = Beer.objects.aggregate(Sum('qty'))['qty__sum'] or 0
    context = {
        'num_visits': num_visits,
        'num_liters': total_qty,
    }

    return render(request, 'alynas/index.html', context)

def light_beer(request: HttpRequest):
    light_beer_type = models.Type.objects.get(name="Light")
    beers = models.Beer.objects.filter(beer_type=light_beer_type)
    return render(request, 'alynas/light_beer.html', {'beers': beers})

def dark_beer(request: HttpRequest):
    dark_beer_type = models.Type.objects.get(name="Dark")
    beers = models.Beer.objects.filter(beer_type=dark_beer_type)
    return render(request, 'alynas/dark_beer.html', {'beers': beers})

class BeerMeniu(generic.ListView):
    model = models.Beer
    template_name = "alynas/beer_meniu.html"
    context_object_name = 'beer_meniu'
    paginate_by = 10

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context =  super().get_context_data(**kwargs)
        context["search"] = True
        return context
    
    def get_queryset(self) -> QuerySet[Any]:
        queryset =  super().get_queryset()
        query = self.request.GET.get("query")
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(name__istartswith=query)
                )
        return queryset
    

class BeerDetail(generic.ListView):
    model = models.Beer
    template_name = "alynas/beer_detail.html"
