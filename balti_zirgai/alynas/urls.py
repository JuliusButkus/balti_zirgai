from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path("beer/", views.BeerMeniu, name="beer_meniu" ),
    path("beer/<int:pk>/", views.BeerDetail, name="beer_detail")
]