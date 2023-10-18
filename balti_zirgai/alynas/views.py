from typing import Any
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest
from django.db.models.query import QuerySet, Q
from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from . import models
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def index(request: HttpRequest):
    num_visits = request.session.get('num_visits', 1)
    request.session['num_visits'] = num_visits + 1
    context = {
        'num_visits': num_visits,
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

@login_required
def buy_beer(request, beer_id):
    beer = get_object_or_404(models.Beer, pk=beer_id)
    existing_purchase = models.Purchase.objects.filter(beer=beer, buyer=request.user).first()
    if existing_purchase:
        existing_purchase.quantity += 1
        existing_purchase.total_price = existing_purchase.quantity * beer.price
        existing_purchase.save()
    else:
        purchase = models.Purchase(beer=beer, buyer=request.user, quantity=1, total_price=beer.price)
        purchase.save()
    messages.success(request, 'Purchase successful!')
    return redirect('beer_meniu')

@login_required
def my_beer(request):
    purchases = models.Purchase.objects.filter(buyer=request.user)
    return render(request, 'alynas/my_beer.html', {'purchases': purchases})