from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path("beer/", views.BeerMeniu.as_view(), name="beer_meniu" ),
    path("beer/<str:name>/", views.BeerDetail.as_view(), name="beer_detail")
]