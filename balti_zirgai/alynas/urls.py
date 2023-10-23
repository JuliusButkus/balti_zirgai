from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('light-beer/', views.LightBeer.as_view(), name='light_beer'),
    path('dark-beer/', views.DarkBeer.as_view(), name='dark_beer'),
    path("beer/", views.BeerMeniu.as_view(), name="beer_meniu" ),
    path("beer/<str:beer_name>/", views.BeerDetail.as_view(), name="beer_detail"),
    path('buy-beer/<int:beer_id>/', views.buy_beer, name='buy_beer'),
    path('my-beer/', views.my_beer, name='my_beer'),
    path('buy-beer/<int:beer_id>/', views.buy_beer, name='buy_beer'),
    path('buy-all-beers/', views.buy_all_beers, name='buy_all_beers'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('order-detail/<int:pk>/', views.order_detail, name='order_detail'),
    path('beer/<str:beer_name>/', views.beer_detail, name='beer_detail'),
]