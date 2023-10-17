from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('light-beer/', views.light_beer, name='light_beer'),
    path('dark-beer/', views.dark_beer, name='dark_beer'),
    path("beer/", views.BeerMeniu.as_view(), name="beer_meniu" ),
    path("beer/<str:name>/", views.BeerDetail.as_view(), name="beer_detail")
]