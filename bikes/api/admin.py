from django.contrib import admin
from django.utils.translation import ugettext as _
from .models import (
    Rental,
    Order
)


class RentalInline(admin.TabularInline):
    model = Rental


@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return Rental.objects.available()


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = (RentalInline,)

    def get_queryset(self, request):
        return Order.objects.available()
