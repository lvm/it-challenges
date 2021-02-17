#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.utils.translation import ugettext as _
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver
import datetime as dt
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator
)
from .managers import AvailableManager

UserModel = get_user_model()


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, editable=False)

    class Meta:
        abstract = True


class Rental(BaseModel):
    BY_TIME_CHOICES = (
        ('h', _('Hourly')),
        ('d', _('Daily')),
        ('w', _('Weekly')),
    )
    order = models.ForeignKey('Order')
    by_time = models.CharField(
        max_length=1,
        choices=BY_TIME_CHOICES,
        default='h',
    )
    due = models.DateTimeField(blank=True, null=True)
    returned_at = models.DateTimeField(blank=True, null=True)
    price = models.PositiveIntegerField(default=0, editable=False)

    objects = AvailableManager()

    def get_absolute_url(self):
        return reverse('rentals-detail', args=[self.pk, 'json'])

    def __str__(self):
        return "{} (Order: #{})".format(
            dict(Rental.BY_TIME_CHOICES).get(self.by_time),
            self.order.pk
        )

    class Meta:
        ordering = ["-due"]
        verbose_name = _("Rental")
        verbose_name_plural = _("Rentals")


class Order(BaseModel):
    lessee = models.ForeignKey(UserModel, null=True)
    is_family = models.BooleanField(default=False)

    objects = AvailableManager()

    def get_absolute_url(self):
        return reverse('orders-detail', args=[self.pk, 'json'])

    def __str__(self):
        return u"Rented at {created} by {lessee}".format(
            created=self.created_at,
            lessee=self.lessee
        )

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")


@receiver(post_save, sender=Rental)
def update_rental_due(sender, instance, created, **kwargs):
    if created:
        if instance.by_time == 'h':
            instance.due = dt.datetime.now() + dt.timedelta(hours=1)
            instance.price = 5

        if instance.by_time == 'd':
            instance.due = dt.datetime.now() + dt.timedelta(days=1)
            instance.price = 20

        if instance.by_time == 'w':
            instance.due = dt.datetime.now() + dt.timedelta(weeks=1)
            instance.price = 60

        instance.save()


@receiver(post_save, sender=Order)
def update_order_status(sender, instance, created, **kwargs):
    if not created and instance.is_deleted:
        instance.rental_set.available().update(is_deleted=True)
