from django.contrib import admin
from . import models


class TypeAdmin(admin.ModelAdmin):
    list_display = ("name", "detail",)
    list_filter = ("name",)
    

class BeerAdmin(admin.ModelAdmin):
    list_display = ("beer_type", "name", "qty", "price", "detail",)
    list_filter = ("beer_type", "name",)


class OrderAdmin(admin.ModelAdmin):
    list_display = ("qty", "status", "date",)
    list_filter = ("status", "qty",) 


admin.site.register(models.Type, TypeAdmin)
admin.site.register(models.Beer, BeerAdmin)
admin.site.register(models.Order, OrderAdmin)