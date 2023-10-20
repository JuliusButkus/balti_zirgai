from django.db import models
from datetime import datetime
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from tinymce.models import HTMLField
from django.urls import reverse
from django.contrib.auth.models import User


User = get_user_model()


class Type(models.Model):
    name = models.CharField(max_length=20, unique=True)
    detail = models.TextField(max_length=1000, blank=True)
    
    class Meta:
        verbose_name = _("type")
        verbose_name_plural = _("types")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("type_detail", kwargs={"pk": self.pk})

class Beer(models.Model):
    name = models.CharField(max_length=100, unique=True)
    qty = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    detail = models.TextField(max_length=1000, blank=True)
    beer_type = models.ForeignKey(
        Type, verbose_name=_('beer type'),
        on_delete=models.CASCADE,
        related_name="beer"
        )
    
    
    class Meta:
        verbose_name = _("beer")
        verbose_name_plural = _("beers")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("beer_detail", kwargs={"pk": self.pk})
    

order_status =(
    (0, _("pending")),
    (1, _("in progres")),
    (2, _("completed")),
    (3, _("canceled")),
)


class Order(models.Model):
    date = models.DateTimeField(_("date"), auto_now=False, auto_now_add=True)
    drinker = models.ForeignKey(
        User, verbose_name=_("drinker"), 
        on_delete=models.CASCADE,
        null=True, blank=True
        )
    status = models.PositiveIntegerField(_("status"), choices=order_status, default=0)


    class Meta:
        verbose_name = _("order")
        verbose_name_plural = _("orders")

    def __str__(self):
        return f'{self.id}, {self.date}, {self.get_status_display()}'

    def get_absolute_url(self):
        return reverse("order_detail", kwargs={"pk": self.pk})

    def get_total_price(self):
        order_lines = self.orderline_set.all()
        total_price = sum(order_line.qty * order_line.price for order_line in order_lines)
        return total_price

    def get_status_display(self):
        return dict(order_status)[self.status]

class OrderLine(models.Model):
    qty = models.IntegerField(blank=False)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.PositiveIntegerField(_("status"), choices=order_status, default=0)
    beer = models.ForeignKey(
        Beer, verbose_name=_('ordered beer'),
        on_delete=models.CASCADE,
        related_name="orderline"
    )
    order = models.ForeignKey(
        Order, verbose_name=_('order'),
        on_delete=models.CASCADE,
        related_name="orderline_set"
    )

    class Meta:
        verbose_name = _("orderline")
        verbose_name_plural = _("orderlines")

    def __str__(self):
        return f'{self.beer.name}, {self.qty}, {self.get_status_display()}'

    def get_absolute_url(self):
        return reverse("orderline_detail", kwargs={"pk": self.pk})

class Purchase(models.Model):
    beer = models.ForeignKey(Beer, on_delete=models.CASCADE)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    


