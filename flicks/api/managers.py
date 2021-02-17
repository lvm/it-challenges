from django.db import models


class AvailableManager(models.Manager):
    def available(self):
        return self.get_queryset().filter(
            is_deleted=False
        )


class FilmManager(AvailableManager):
    pass


class PersonManager(AvailableManager):
    pass
