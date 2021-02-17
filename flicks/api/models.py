#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from django.template.defaultfilters import slugify
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.core.urlresolvers import (
    reverse,
    reverse_lazy
)
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator
)
from datetime import datetime
from .managers import (
    FilmManager,
    PersonManager,
)
import roman

UserModel = get_user_model()


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, editable=False)

    class Meta:
        abstract = True


class Film(BaseModel):
    title = models.CharField(max_length=255)
    year = models.PositiveIntegerField(
        default=datetime.now().year,
        validators=[
            # Film history suggests this was the decade where it all started
            MinValueValidator(1800),
            MaxValueValidator(datetime.now().year)
        ]
    )

    objects = FilmManager()

    def in_roman(self):
        return roman.toRoman(self.year)

    def get_absolute_url(self):
        return reverse('film-detail', args=[self.pk, 'json'])

    def __str__(self):
        return u"{title} ({year})".format(
            title=self.title,
            year=self.year
        )

    class Meta:
        ordering = ["-year"]
        verbose_name = _("Film")
        verbose_name_plural = _("Films")


class Person(BaseModel):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    alias = models.CharField(
        max_length=255,
        help_text=_("May contain several values separated by comma."))
    as_actor = models.ManyToManyField("Film",
                                      related_name="as_actor",
                                      blank=True)
    as_director = models.ManyToManyField("Film",
                                         related_name="as_director",
                                         blank=True)
    as_producer = models.ManyToManyField("Film",
                                         related_name="as_producer",
                                         blank=True)

    objects = PersonManager()

    def aliases(self):
        return map(lambda a: a.strip(), self.alias.split(','))

    def get_absolute_url(self):
        return reverse('person-detail', args=[self.pk, 'json'])

    def __str__(self):
        return u"{last}, {first}".format(
            last=self.last_name,
            first=self.first_name
        )

    class Meta:
        verbose_name = _("Person")
        verbose_name_plural = _("People")
