from typing import Any
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest
from django.db.models.query import QuerySet, Q
from django.shortcuts import render, get_object_or_404
from django.views import generic
from . import models


def index(request: HttpRequest):
    num_visits = request.session.get('num_visits', 1)
    request.session['num_visits'] = num_visits + 1
    context = {
        'num_visits': num_visits,
    }
    return render(request, 'library/index.html', context)

class BeerMeniu(generic.ListView):
    model = models.Beer
    template_name = "library/beer_meniu.html"
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
    template_name = "library/beer_detail.html"