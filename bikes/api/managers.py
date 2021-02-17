from django.db import models


class AvailableManager(models.Manager):
    def available(self):
        return self.get_queryset().filter(
            is_deleted=False
        )


class RentalManager(AvailableManager):
    def for_user(self, user):
        return self.available().filter(order__lessee=user)


class OrderManager(AvailableManager):
    def for_user(self, user):
        return self.available().filter(lessee=user)
