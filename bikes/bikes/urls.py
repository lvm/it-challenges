from django.conf.urls import (
    url,
    include,
)
from django.views.generic.base import RedirectView
from rest_framework import routers
from api.api_views import (
    UserCreateView,
    UserLoginView,
    UserLogoutView,
    OrderViewSet,
    RentalViewSet
)

router = routers.DefaultRouter()
router.register(r'orders', OrderViewSet)
router.register(r'rentals', RentalViewSet)

urlpatterns = [
    url(r'^$',
        RedirectView.as_view(url='/api/', permanent=True),
        name='index'),
    url(r'^api/', include(router.urls)),
    url(r'^api/users/create(/)?$',
        UserCreateView.as_view(), name='user-create'),
    url(r'^api/users/login(/)?$',
        UserLoginView.as_view(), name='user-login'),
    url(r'^api/users/logout(/)?$',
        UserLogoutView.as_view(), name='user-logout'),
]
