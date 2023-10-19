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
    num_types = Type.objects.count()
    context = {
        'num_visits': num_visits,
        'num_liters': total_qty,
        'num_types': num_types,
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
                Q(name__icontains=query) |
                Q(name__istartswith=query)
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
        messages.success(request, f'Added {quantity} {beer.name} successfully!')
        return redirect('beer_meniu')
    return render(request, 'alynas/beer_detail.html', {'object_list': [beer]})


@login_required
def buy_all_beers(request):
    purchases = models.Purchase.objects.filter(buyer=request.user)
    total_price = sum(purchase.total_price for purchase in purchases)

    order = models.Order.objects.create(drinker=request.user)

    for purchase in purchases:
        beer = purchase.beer
        quantity = purchase.quantity
        price = purchase.total_price

        order_line = models.OrderLine.objects.create(
            qty=quantity,
            price=price,
            status=1,
            beer=beer,
            order=order,
        )

        beer.qty -= quantity
        beer.save()

        purchase.delete()

    messages.success(request, f'Purchased all beers successfully for a total price of {total_price}!')
    return redirect('my_orders')


@login_required
def my_beer(request):
    purchases = models.Purchase.objects.filter(buyer=request.user)
    total_price = sum(purchase.total_price for purchase in purchases)
    return render(request, 'alynas/my_beer.html', {'purchases': purchases, 'total_price': total_price})

@login_required
def my_orders(request):
    user_orders = models.Order.objects.filter(drinker=request.user)
    order_data = []
    for order in user_orders:
        order_lines = order.orderline_set.all()
        total_price = sum(item.qty * item.price for item in order_lines)
        order_data.append({
            'order': order,
            'order_lines': order_lines,
            'total_price': total_price
        })
    return render(request, 'alynas/my_orders.html', {'order_data': order_data})

def order_detail(request, pk):
    order = get_object_or_404(models.Order, pk=pk)
    order_lines = models.OrderLine.objects.filter(order=order)
    for order_line in order_lines:
        order_line.total_price = order_line.qty * order_line.price
    return render(request, 'alynas/order_detail.html', {'order': order, 'order_lines': order_lines})