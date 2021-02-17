from django.contrib import admin
from django.utils.translation import ugettext as _
from .models import (
    Film,
    Person
)


@admin.register(Film)
class FilmAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return Film.objects.available()


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return Person.objects.available()

    def get_field_queryset(self, db, db_field, request):
        if db_field.name in map(
                lambda r: "as_{}".format(r),
                ['actor', 'director', 'producer']):
            return db_field.remote_field.model._default_manager.available()

        super().get_field_queryset(db, db_field, request)
