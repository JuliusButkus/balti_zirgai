from typing import Any
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.db.models.query import QuerySet, Q
from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from . import models, forms
from .models import Beer, Type
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import DetailView
from django.urls import reverse_lazy


def index(request: HttpRequest):
    num_visits = request.session.get('num_visits', 1)
    request.session['num_visits'] = num_visits + 1
    total_qty = Beer.objects.aggregate(Sum('qty'))['qty__sum'] or 0
    num_types = Type.objects.count()
    num_light_beer = len(set(Beer.objects.filter(beer_type__name='Light').values_list('name', flat=True)))
    num_dark_beer = len(set(Beer.objects.filter(beer_type__name='Dark').values_list('name', flat=True)))
    context = {
        'num_visits': num_visits,
        'num_liters': total_qty,
        'num_beer': num_types,
        'num_light_beer': num_light_beer,
        'num_dark_beer': num_dark_beer,

    }

    return render(request, 'alynas/index.html', context)

class LightBeer(generic.ListView):
    model = models.Beer
    template_name = "alynas/light_beer.html"
    context_object_name = 'light_beer'
    light_beer_type = models.Type.objects.get(name="Light")
    beers = models.Beer.objects.filter(beer_type=light_beer_type)
    paginate_by = 5

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
   
class DarkBeer(generic.ListView):
    model = models.Beer
    template_name = "alynas/dark_beer.html"
    context_object_name = 'dark_beer'
    dark_beer_type = models.Type.objects.get(name="Dark")
    beers = models.Beer.objects.filter(beer_type=dark_beer_type)
    paginate_by = 5

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
    

class BeerDetail(generic.edit.FormMixin, DetailView):
    model = Beer
    template_name = "alynas/beer_detail.html"
    context_object_name = 'beer'
    form_class = forms.BeerReviewForm

    def get_initial(self) -> dict[str, Any]:
        initial = super().get_initial()
        initial['beer'] = self.get_object()
        initial['reviewer'] = self.request.user
        return initial

    def post(self, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form) -> HttpResponse:
        form.instance.beer = self.object
        form.instance.reviewer = self.request.user
        form.save()
        messages.success(self.request, 'Review posted success')
        return super().form_valid(form)
    
    def get_success_url(self) -> str:
        return reverse_lazy('beer_detail', kwargs={'beer_name': self.get_object().name})
    

    def get_object(self, queryset=None):
        return Beer.objects.get(name=self.kwargs['beer_name'])


@login_required
def buy_beer(request, beer_id):
    beer = get_object_or_404(models.Beer, pk=beer_id)
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > beer.qty:
            messages.warning(request, f'Sorry, only {beer.qty} units of this beer are available.')
        else:
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
    order_data = models.Order.objects.filter(drinker=request.user)
    return render(request, 'alynas/my_beer.html', {'purchases': purchases, 'total_price': total_price, 'order_data': order_data})
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

def beer_detail(request: HttpRequest, pk: int):
    return render(
        request,
        'alynas/beer_detail.html',
        {'beer': get_object_or_404(models.Beer, pk=pk)}
    )