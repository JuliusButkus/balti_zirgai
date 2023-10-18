from typing import Any
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest
from django.db.models.query import QuerySet, Q
from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from . import models
from .models import Beer, Type
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import DetailView




def index(request: HttpRequest):
    num_visits = request.session.get('num_visits', 1)
    request.session['num_visits'] = num_visits + 1
    total_qty = Beer.objects.aggregate(Sum('qty'))['qty__sum'] or 0
    num_beer = Beer.objects.count()
    context = {
        'num_visits': num_visits,
        'num_liters': total_qty,
        'num_beer': num_beer,
    }

    return render(request, 'alynas/index.html', context)

def light_beer(request: HttpRequest):
    light_beer_type = models.Type.objects.get(name="Light")
    beers = models.Beer.objects.filter(beer_type=light_beer_type)
    paginate_by = 5
    paginator = Paginator(beers, paginate_by)
    page = request.GET.get('page')
    try:
        beers = paginator.get_page(page)
    except EmptyPage:
        beers = paginator.get_page(1)
    return render(request, 'alynas/light_beer.html', {'beers': beers},)

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
                Q(name__icontains=query)
                )
        return queryset
    

class BeerDetail(DetailView):
    model = Beer
    template_name = "alynas/beer_detail.html"
    context_object_name = 'beer'

    def get_object(self, queryset=None):
        return Beer.objects.get(name=self.kwargs['beer_name'])


@login_required
def buy_beer(request, beer_id):
    beer = get_object_or_404(models.Beer, pk=beer_id)
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        total_price = beer.price * quantity
        existing_purchase = models.Purchase.objects.filter(beer=beer, buyer=request.user).first()
        if existing_purchase:
            existing_purchase.quantity += quantity
            existing_purchase.total_price += total_price
            existing_purchase.save()
        else:
            purchase = models.Purchase(beer=beer, buyer=request.user, quantity=quantity, total_price=total_price)
            purchase.save()
        messages.success(request, f'Purchased {quantity} {beer.name}(s) successfully!')
        return redirect('my_beer')
    return render(request, 'alynas/beer_detail.html', {'object_list': [beer]})


@login_required
def my_beer(request):
    purchases = models.Purchase.objects.filter(buyer=request.user)
    total_price = sum(purchase.total_price for purchase in purchases)
    return render(request, 'alynas/my_beer.html', {'purchases': purchases, 'total_price': total_price})