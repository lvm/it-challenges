from django.conf import settings
from django.db.models import Sum
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
import datetime as dt
from .models import (
    Order,
    Rental
)

UserModel = get_user_model()


class StringArrayField(serializers.ListField):
    def to_representation(self, obj):
        obj = super().to_representation(self, obj)
        return ",".join([str(element) for element in obj])

    def to_internal_value(self, data):
        data = map(lambda a: a.strip(), data.split(','))
        return super().to_internal_value(data)


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=UserModel.objects.all())]
    )
    password = serializers.CharField(min_length=8, write_only=True)

    class Meta:
        model = UserModel
        fields = ('id', 'username', 'password')


class RentalSerializer(serializers.ModelSerializer):
    rental_type = serializers.SerializerMethodField()
    returned = serializers.BooleanField(default=False, write_only=True)
    is_returned = serializers.SerializerMethodField()

    def get_rental_type(self, obj):
        return dict(Rental.BY_TIME_CHOICES).get(obj.by_time)

    def get_is_returned(self, obj):
        return True if obj.returned_at else False

    def update(self, instance, validated_data):
        if validated_data.get('returned', None):
            instance.returned_at = dt.datetime.now()
        else:
            instance.returned_at = None

        instance.save()

        return instance

    class Meta:
        model = Rental
        fields = ('id', 'rental_type', 'price', 'due',
                  'is_returned', 'returned')


class OrderSerializer(serializers.ModelSerializer):
    bike_rentals = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()
    rentals = StringArrayField(write_only=True)

    def get_bike_rentals(self, obj):
        return RentalSerializer(
            obj.rental_set.available(),
            many=True
        ).data

    def get_total(self, obj):
        subtotal = obj.rental_set.available().aggregate(
            Sum('price')
        ).get('price__sum')
        total = subtotal
        if obj.is_family:
            total = subtotal - (subtotal * 0.3)
        return {'total': total, 'subtotal': subtotal}

    def create(self, validated_data):
        is_family = True if validated_data.get('is_family', None) else False
        rental_list = validated_data.get('rentals', None)
        order = Order()
        if rental_list:
            order = Order.objects.create(
                lessee=self.context.get('request').user,
                is_family=is_family
            )
            for r_type in filter(lambda r: r, rental_list):
                Rental.objects.create(by_time=r_type, order=order)

        return order

    class Meta:
        model = Order
        fields = ('id', 'url', 'rentals',
                  'lessee', 'is_family',
                  'bike_rentals', 'total')
