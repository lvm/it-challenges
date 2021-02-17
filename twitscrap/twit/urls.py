from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
import views

urlpatterns = [
    url(r'^(?P<username>[\w]+)?$', views.users),
]

urlpatterns = format_suffix_patterns(urlpatterns)
