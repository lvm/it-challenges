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
    FilmViewSet,
    PersonViewSet,
)

router = routers.DefaultRouter()
router.register(r'films', FilmViewSet)
router.register(r'people', PersonViewSet)

urlpatterns = [
    url(r'^$',
        RedirectView.as_view(url='/api/', permanent=True),
        name='index'),
    url(r'^api/for-humans/', include('rest_framework_docs.urls')),
    url(r'^api/', include(router.urls)),
    url(r'^api/users/create(/)?$',
        UserCreateView.as_view(), name='user-create'),
    url(r'^api/users/login(/)?$',
        UserLoginView.as_view(), name='user-login'),
    url(r'^api/users/logout(/)?$',
        UserLogoutView.as_view(), name='user-logout'),
]
